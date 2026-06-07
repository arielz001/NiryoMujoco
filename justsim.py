import tkinter as tk
from tkinter import ttk
import numpy as np

# --- 1. CONFIGURACIÓN DEL GEMELO DIGITAL ---
FILENAME = "cmd_joints.txt"

# Pose inicial por defecto para el simulador (en grados)
INITIAL_POSE_DEG = [0, 29, -72, 0, 0, 0]

# Límites de movimiento de las articulaciones (en grados)
JOINT_RANGES = [
    (-90, 90),    # J1
    (-50, 30),    # J2
    (-50, 120),  # J3
    (-90, 90),    # J4
    (-80, 80),    # J5
    (-50, 50)     # J6
]

# --- 2. CREACIÓN DE LA INTERFAZ GRÁFICA (Tkinter) ---
root = tk.Tk()
root.title("Panel Control - Niryo Gemelo Digital (Simulación)")
root.geometry("480x520")
root.configure(bg='#222222')

style = ttk.Style()
style.configure("TLabel", foreground="white", background="#222222", font=("Arial", 11))

title_lbl = ttk.Label(root, text="Control Gemelo Digital (MuJoCo)", font=("Arial", 14, "bold"))
title_lbl.pack(pady=15)

sliders = []
label_values = []

def send_to_txt(*args):
    """Convierte los valores de los sliders a radianes y actualiza el archivo para MuJoCo"""
    rad_vals = []
    
    # Procesar los 6 joints del brazo
    for i in range(6):
        deg = sliders[i].get()
        label_values[i].config(text=f"{int(deg)}°")
        rad_vals.append(np.radians(deg))
    
    # Procesar la garra/pinza
    g_val = slider_g.get()
    val_lbl_g.config(text=f"{g_val:.3f}")
    rad_vals.append(g_val)
    
    # Formatear línea única separada por comas para el lector de MuJoCo
    line = ",".join([f"{x:.6f}" for x in rad_vals])
    try:
        with open(FILENAME, "w") as f:
            f.write(line)
    except Exception as e:
        print(f"Error al escribir en el archivo de simulación: {e}")

# Crear Sliders para las 6 articulaciones (Joints)
joint_names = ["Joint 1", "Joint 2", "Joint 3", "Joint 4", "Joint 5", "Joint 6"]
for i in range(6):
    frame = tk.Frame(root, bg='#222222', pady=5)
    frame.pack(fill='x', padx=20)
    
    lbl = ttk.Label(frame, text=joint_names[i], width=10)
    lbl.pack(side='left')
    
    slider = tk.Scale(frame, from_=JOINT_RANGES[i][0], to=JOINT_RANGES[i][1], orient='horizontal', 
                      bg='#333333', fg='white', highlightbackground='#222222',
                      troughcolor='#555555', command=send_to_txt)
    
    slider.set(INITIAL_POSE_DEG[i])  
    slider.pack(side='left', fill='x', expand=True, padx=10)
    sliders.append(slider)
    
    val_lbl = ttk.Label(frame, text=f"{INITIAL_POSE_DEG[i]}°", width=6)
    val_lbl.pack(side='right')
    label_values.append(val_lbl)

# Slider para el control de la Garra
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

# --- 3. CIERRE SEGURO Y ARRANQUE ---
def on_close():
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# Escribe los valores iniciales en el archivo de texto al arrancar la interfaz
send_to_txt()

root.mainloop()