from pyniryo import *
import tkinter as tk
from tkinter import ttk
import numpy as np
import os

# --- 1. CONEXIÓN E INICIALIZACIÓN DEL ROBOT REAL ---
ROBOT_IP = "10.10.10.10"
FILENAME = "cmd_joints.txt"

# Pose por defecto para inicializar la UI SOLO si el robot real está apagado/desconectado
FALLBACK_POSE_DEG = [0, 29, -72, 0, 0, 0]

try:
    print(f"Conectando al Niryo Ned2 en {ROBOT_IP}...")
    robot = NiryoRobot(ROBOT_IP)
    robot.calibrate_auto()
    robot.update_tool()
    robot.release_with_tool()
    robot_connected = True
    print("¡Robot real conectado y calibrado con éxito!")
except Exception as e:
    print(f"Advertencia: No se pudo conectar al robot real ({e}). Corriendo en modo SOLO SIMULACIÓN.")
    robot_connected = False

# --- 2. CONFIGURACIÓN DE LÍMITES EN GRADOS ---
JOINT_RANGES = [
    (-90, 90), # J1
    (-50, 30), # J2
    (-120, 120), # J3
    (-90, 90), # J4
    (-80, 80), # J5
    (-50, 50)  # J6
]

initial_pose_deg = list(FALLBACK_POSE_DEG) #

if robot_connected:
    try:
        # Leemos la posición real en la que el robot está parado actualmente
        joints_rad = robot.get_joints()
        initial_pose_deg = [int(np.degrees(j)) for j in joints_rad]
        print(f"Sincronizando interfaz con la pose real del hardware: {initial_pose_deg}")
    except Exception as e:
        print(f"No se pudo leer la pose inicial del robot, usando valores por defecto: {e}")

# --- 4. CREACIÓN DE LA INTERFAZ GRÁFICA (Tkinter) ---
root = tk.Tk()
root.title("Panel Control Unificado - Niryo Gemelo Digital")
root.geometry("480x620")
root.configure(bg='#222222')

style = ttk.Style()
style.configure("TLabel", foreground="white", background="#222222", font=("Arial", 11))

title_lbl = ttk.Label(root, text="Control Unificado (Real + MuJoCo)", font=("Arial", 14, "bold"))
title_lbl.pack(pady=15)

sliders = []
label_values = []

def send_to_txt(*args):
    """Convierte los sliders a radianes y escribe en el TXT para MuJoCo en tiempo real"""
    rad_vals = []
    for i in range(6):
        deg = sliders[i].get()
        label_values[i].config(text=f"{int(deg)}°")
        rad_vals.append(np.radians(deg))
    
    # Agregar la garra
    g_val = slider_g.get()
    val_lbl_g.config(text=f"{g_val:.3f}")
    rad_vals.append(g_val)
    
    # Escribir línea única separada por comas para MuJoCo
    line = ",".join([f"{x:.6f}" for x in rad_vals])
    try:
        with open(FILENAME, "w") as f:
            f.write(line)
    except Exception:
        pass

# Crear Sliders de los 6 Joints cargando la pose inicial calculada
joint_names = ["Joint 1", "Joint 2", "Joint 3", "Joint 4", "Joint 5", "Joint 6"]
for i in range(6):
    frame = tk.Frame(root, bg='#222222', pady=5)
    frame.pack(fill='x', padx=20)
    
    lbl = ttk.Label(frame, text=joint_names[i], width=10)
    lbl.pack(side='left')
    
    slider = tk.Scale(frame, from_=JOINT_RANGES[i][0], to=JOINT_RANGES[i][1], orient='horizontal', 
                      bg='#333333', fg='white', highlightbackground='#222222',
                      troughcolor='#555555', command=send_to_txt)
    
    # Aseguramos que el slider tome el valor real donde está parado el robot
    slider.set(initial_pose_deg[i])  
    slider.pack(side='left', fill='x', expand=True, padx=10)
    sliders.append(slider)
    
    val_lbl = ttk.Label(frame, text=f"{initial_pose_deg[i]}°", width=6)
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

# --- 5. ACCIONES DE LOS BOTONES ---
def move_robot():
    """Toma los valores actuales de los sliders y ejecuta el movimiento en el robot real"""
    joints_rad = [np.radians(slider.get()) for slider in sliders]
    
    if robot_connected:
        try:
            robot.move_joints(joints_rad)
            print("¡Robot Real movido exitosamente a:", [int(np.degrees(j)) for j in joints_rad], "grados!")
        except Exception as e:
            print(f"Error al mover el robot real: {e}")
    else:
        print("Modo simulación activado: El robot real no está conectado.")
    
    send_to_txt()

def refresh():
    """Lee la pose actual del hardware y actualiza la UI y el archivo de texto"""
    if robot_connected:
        try:
            joints_rad = robot.get_joints()
            print(f"Actual joints desde hardware (rad): {joints_rad}")
            for i in range(6):
                deg_val = np.degrees(joints_rad[i])
                deg_val = max(JOINT_RANGES[i][0], min(deg_val, JOINT_RANGES[i][1]))
                sliders[i].set(int(deg_val))
            send_to_txt()
        except Exception as e:
            print(f"Error al leer el hardware: {e}")
    else:
        print("No hay ningún robot real conectado para leer su pose.")

# Botones de control inferiores
frame_buttons = tk.Frame(root, bg='#222222', pady=15)
frame_buttons.pack()

btn_move = tk.Button(frame_buttons, text="Move", width=12, highlightbackground='#222222', command=move_robot)
btn_move.pack(pady=4)

btn_read = tk.Button(frame_buttons, text="Read Current Pose", width=20, highlightbackground='#222222', command=refresh)
btn_read.pack(pady=4)

# --- 6. CIERRE SEGURO ---
def on_close():
    if robot_connected:
        robot.close_connection()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# Escribe la primera línea en el TXT para que MuJoCo imite la pose actual del robot real
send_to_txt()

root.mainloop()