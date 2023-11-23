import os
import pydicom
import nibabel as nib
import numpy as np
import nrrd
import sys
import subprocess

def try_read_dicom(file_path):
    try:
        return pydicom.dcmread(file_path)
    except pydicom.errors.InvalidDicomError:
        return None

def dicom_to_nifti(dicom_folder, output_filename):
    dicom_files = [f for f in (try_read_dicom(os.path.join(dicom_folder, file)) for file in os.listdir(dicom_folder) if os.path.isfile(os.path.join(dicom_folder, file))) if f is not None]
    if not dicom_files:
        raise ValueError("Nenhum arquivo DICOM válido encontrado no diretório fornecido.")
    dicom_files.sort(key=lambda x: int(x.InstanceNumber) if x.InstanceNumber is not None else 0)
    if len(set([d.pixel_array.shape for d in dicom_files])) > 1:
        raise ValueError("Arquivos DICOM com dimensões inconsistentes.")
    dicom_data = np.stack([s.pixel_array for s in dicom_files])
    pixel_spacing = dicom_files[0].PixelSpacing
    slice_thickness = dicom_files[0].SliceThickness
    affine = np.eye(4)
    affine[0, 0], affine[1, 1], affine[2, 2] = pixel_spacing[1], pixel_spacing[0], float(slice_thickness)
    nifti_image = nib.Nifti1Image(dicom_data, affine)
    nib.save(nifti_image, output_filename)

def nifti_to_nrrd(nifti_file, nrrd_output_file):
    nifti_image = nib.load(nifti_file)
    data = nifti_image.get_fdata()
    nrrd_metadata = {
        'space': 'right-anterior-superior',
        'kinds': ['domain', 'domain', 'domain'],
        'space directions': nifti_image.affine[:3, :3],
        'space origin': nifti_image.affine[:3, 3]
    }
    nrrd.write(nrrd_output_file, data, header=nrrd_metadata)
    print(f"Arquivo NRRD convertido e salvo em: {nrrd_output_file}")

def segmentar_task(task, nifti_file, output_dir):
    # Comando para executar o TotalSegmentator com a task especificada no modo fast usando CPU
    command = [
        "TotalSegmentator",
        "-i", nifti_file,
        "-o", output_dir,
        "-ta", task,
        "--fast",  # Adiciona a opção --fast para usar o modelo de baixa resolução
        "--device", "cpu"  # Força o uso da CPU
    ]
    subprocess.run(command)

    # Aqui, assumimos que o TotalSegmentator cria um arquivo chamado 'output.nii' no output_dir
    nifti_result_file = os.path.join(output_dir, "output.nii")
    nrrd_file = os.path.join(output_dir, f"{task}_segmentation.nrrd")
    nifti_to_nrrd(nifti_result_file, nrrd_file)


def combinar_subclasses(subclasses, input_dir, output_file):
    # Comando para executar o totalseg_combine_masks com as subclasses especificadas
    subprocess.run(["totalseg_combine_masks", "-i", input_dir, "-o", output_file, "-m"] + subclasses)


def main():
    # Verifica se o número de argumentos está correto
    if len(sys.argv) < 5:
        print("Uso: python seg.py <input_path> <output_path> <operation> [task|subclasses]")
        sys.exit(1)

    input_path, output_path, operation = sys.argv[1:4]
    
    # Verifica se o diretório de entrada contém imagens DICOM
    if not os.listdir(input_path):
        print("O diretório não contém imagens DICOM.")
        sys.exit(1)
        
    # Cria o diretório de saída se ele não existir
    os.makedirs(output_path, exist_ok=True)
    
    # Gera o caminho do arquivo NIFTI de saída
    nifti_filename = os.path.join(output_path, "output.nii")
    
    # Converte os arquivos DICOM para NIFTI
    dicom_to_nifti(input_path, nifti_filename)

    # Decide qual operação executar
    if operation == "segmentar_task":
        task = sys.argv[4]
        segmentar_task(task, nifti_filename, output_path)
    elif operation == "combinar_subclasses":
        subclasses = sys.argv[4:]
        nrrd_filename = os.path.join(output_path, "combined_mask.nrrd")
        combinar_subclasses(subclasses, output_path, nrrd_filename)
    else:
        print(f"Operação desconhecida: {operation}")
        sys.exit(1)

if __name__ == '__main__':
    main()
