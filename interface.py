import tkinter as tk
from tkinter import ttk
import numpy as np

# Rangos de joints en grados del Niryo Ned2 reales
JOINT_RANGES = [
    (-168, 168), # J1
    (-104, 34),  # J2
    (-160, 130),   # J3
    (-119, 119), # J4
    (-110, 110), # J5
    (-145, 145)  # J6
]
# Pose inicial equivalente a la tuya (0, 29, -72, 0, 0, 0)
INIT_DEGS = [0, 29, -150, 0, 0, 0]
FILENAME = "cmd_joints.txt"

root = tk.Tk()
root.title("Panel Control Externo - Niryo")
root.geometry("460x560")
root.configure(bg='#222222')

style = ttk.Style()
style.configure("TLabel", foreground="white", background="#222222", font=("Arial", 11))

title_lbl = ttk.Label(root, text="Panel de Control de Articulaciones", font=("Arial", 14, "bold"))
title_lbl.pack(pady=15)

sliders = []
label_values = []

def send_to_txt(*args):
    """Convierte los sliders a radianes y los escribe en el archivo txt"""
    rad_vals = []
    for i in range(6):
        deg = sliders[i].get()
        label_values[i].config(text=f"{int(deg)}°")
        rad_vals.append(np.radians(deg))
    
    # Agregar la garra
    g_val = slider_g.get()
    val_lbl_g.config(text=f"{g_val:.3f}")
    rad_vals.append(g_val)
    
    # Escribir línea única separada por comas
    line = ",".join([f"{x:.6f}" for x in rad_vals])
    with open(FILENAME, "w") as f:
        f.write(line)

# Crear Sliders
joint_names = ["Joint 1", "Joint 2", "Joint 3", "Joint 4", "Joint 5", "Joint 6"]
for i in range(6):
    frame = tk.Frame(root, bg='#222222', pady=5)
    frame.pack(fill='x', padx=20)
    
    lbl = ttk.Label(frame, text=joint_names[i], width=10)
    lbl.pack(side='left')
    
    slider = tk.Scale(frame, from_=JOINT_RANGES[i][0], to=JOINT_RANGES[i][1], orient='horizontal', 
                      bg='#333333', fg='white', highlightbackground='#222222',
                      troughcolor='#555555', command=send_to_txt)
    slider.set(INIT_DEGS[i])
    slider.pack(side='left', fill='x', expand=True, padx=10)
    sliders.append(slider)
    
    val_lbl = ttk.Label(frame, text=f"{INIT_DEGS[i]}°", width=6)
    val_lbl.pack(side='right')
    label_values.append(val_lbl)

# Slider para la Garra
frame_g = tk.Frame(root, bg='#222222', pady=10)
frame_g.pack(fill='x', padx=20)
lbl_g = ttk.Label(frame_g, text="Garra 1", width=10)
lbl_g.pack(side='left')

slider_g = tk.Scale(frame_g, from_=0.0, to=0.02, resolution=0.001, orient='horizontal', 
                    bg='#333333', fg='white', highlightbackground='#222222',
                    troughcolor='#555555', command=send_to_txt)
slider_g.set(0.010)
slider_g.pack(side='left', fill='x', expand=True, padx=10)

val_lbl_g = ttk.Label(frame_g, text="0.010", width=6)
val_lbl_g.pack(side='right')

# Botones informativos (Al hacer click imprimen en la consola de la UI)
frame_buttons = tk.Frame(root, bg='#222222', pady=20)
frame_buttons.pack()

def print_current():
    with open(FILENAME, "r") as f:
        data = f.read().strip().split(",")
        print(f"\nJointsPosition({', '.join(data[:6])}, metadata=JointsPositionMetadata.v1())")

btn_move = tk.Button(frame_buttons, text="Move", width=12, highlightbackground='#222222')
btn_move.pack(pady=4)

btn_read = tk.Button(frame_buttons, text="Read Current Pose", width=20, 
                         highlightbackground='#222222', command=print_current)
btn_read.pack(pady=4)

# Primera escritura al arrancar
send_to_txt()

root.mainloop()