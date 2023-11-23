import tkinter as tk
from tkinter import ttk
import subprocess
import os
from tasks_disponiveis import tasks_disponiveis
from body_subclasses import body_subclasses
from cerebral_bleed_subclasses import cerebral_bleed_subclasses
from coronary_arteries_subclasses import coronary_arteries_subclasses
from hip_implant_subclasses import hip_implant_subclasses
from lung_vessels_subclasses import lung_vessels_subclasses
from pleural_pericard_effusion_subclasses import pleural_pericard_effusion_subclasses
from total_subclasses import total_subclasses

# Caminho para o script de segmentação
script_segmentacao = "seg.py"

# Caminho das imagens DICOM
input_path = "C:/Users/rapha/OneDrive/Área de Trabalho/Facul Prog/Segmentacao/CT"

# Diretório de saída para segmentações ou combinação de subclasses
output_dir = "C:/Users/rapha/OneDrive/Área de Trabalho/Facul Prog/Segmentacao/CT/BinaryMask"

# Função para executar o script de segmentação
def run_segmentation(operacao, task=None, subclasses=None):
    os.makedirs(output_dir, exist_ok=True)
    
    if operacao == "segmentar_task" and task is not None:
        comando = ["python", script_segmentacao, input_path, output_dir, operacao, task]
    elif operacao == "combinar_subclasses" and subclasses is not None:
        comando = ["python", script_segmentacao, input_path, output_dir, operacao] + subclasses
    else:
        print("Operação ou parâmetros inválidos.")
        return

    subprocess.run(comando)

# Função para abrir a janela de escolha da task
def abrir_janela_task():
    janela_task = tk.Toplevel(root)
    janela_task.title("Escolher Task")
    janela_task.state('zoomed')  # Maximiza a janela secundária
    ttk.Label(janela_task, text="Escolha a Task:").pack(pady=10)
    combo_task = ttk.Combobox(janela_task, values=tasks_disponiveis, state="readonly")
    combo_task.pack(pady=5)
    ttk.Button(janela_task, text="Segmentar", command=lambda: run_segmentation("segmentar_task", task=combo_task.get())).pack(pady=10)

#Funcao para abrir janela de combinacoes
def abrir_janela_combinar():
    janela_combinar = tk.Toplevel(root)
    janela_combinar.title("Combinar Subclasses")
    width = root.winfo_screenwidth() * 0.9
    height = root.winfo_screenheight() * 0.9
    janela_combinar.geometry(f"{int(width)}x{int(height)}+{int(width*0.05)}+{int(height*0.05)}")

    # Frame para os checkboxes com scrollbar
    frame_scroll = tk.Frame(janela_combinar)
    frame_scroll.pack(fill=tk.BOTH, expand=1)
    
    canvas = tk.Canvas(frame_scroll)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
    
    scrollbar = ttk.Scrollbar(frame_scroll, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    
    frame_checkboxes = tk.Frame(canvas)
    
    canvas.create_window((0, 0), window=frame_checkboxes, anchor="nw")
    
    checkboxes = {}
    for subclass in total_subclasses:
        checkboxes[subclass] = tk.BooleanVar()
        tk.Checkbutton(frame_checkboxes, text=subclass, variable=checkboxes[subclass]).pack(anchor=tk.W)

    # Botão fora do frame dos checkboxes
    ttk.Button(janela_combinar, text="Confirmar", command=lambda: confirmar_combinacao(checkboxes)).pack(pady=10)

    janela_combinar.mainloop()
# Função que é chamada quando o botão "Confirmar" é clicado
def confirmar_combinacao(checkboxes):
    subclasses_selecionadas = [k for k, v in checkboxes.items() if v.get()]
    if subclasses_selecionadas:
        run_segmentation("combinar_subclasses", subclasses=subclasses_selecionadas)
    else:
        print("Nenhuma subclasse selecionada.")

# Função chamada para decidir o tipo de segmentação
def escolher_segmentacao():
    escolha = combo_escolha.get()
    if escolha == "Segmentar Task":
        abrir_janela_task()
    elif escolha == "Combinar Subclasses":
        abrir_janela_combinar()

# Cria a janela principal
root = tk.Tk()
root.title("Segmentador de Órgãos")
root.state('zoomed')
frame = ttk.Frame(root)
frame.pack(padx=10, pady=10)

opcoes = ["Segmentar Task", "Combinar Subclasses"]
combo_escolha = ttk.Combobox(frame, values=opcoes, state="readonly")
combo_escolha.pack(pady=5)

ttk.Button(frame, text="Continuar", command=escolher_segmentacao).pack(pady=10)

root.mainloop()
