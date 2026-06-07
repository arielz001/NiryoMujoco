import tkinter as tk
from tkinter import ttk
import numpy as np

# --- 1. CONFIGURACIÓN DEL GEMELO DIGITAL ---
FILENAME = "cmd_joints.txt"

# Límites de movimiento de las articulaciones (en grados)
JOINT_RANGES = [
    (-90, 90), (-50, 30), (-50, 120), (-90, 90), (-80, 80), (-50, 50)
]

# --- 2. SECUENCIA PICK AND PLACE CORREGIDA (Pick en -90° y Place en 90°) ---
# Formato de cada pose: [J1, J2, J3, J4, J5, J6, Garra]
SECUENCIA = [
    {"desc": "1. Posición de Reposo / Inicio", "pose": [0, 29, -72, 0, 0, 0, 0.020]},
    
    # --- FASE DE ACERCARSE AL OBJETO EN -90° ---
    {"desc": "2. Girar a la zona de Pick (-90°)", "pose": [-90, 29, -72, 0, 0, 0, 0.020]},
    {"desc": "3. Bajar a buscar el objeto en -90°", "pose": [-90, 25, -55, 0, 0, 0, 0.020]},
    {"desc": "4. ¡Cerrar Pinza! (Pick)", "pose": [-90, -22, -50, 0, 0, 0, 0.002]},
    
    # --- FASE DE SUBIDA (Elevación de seguridad en -90°) ---
    {"desc": "5. Alzar el brazo verticalmente con el objeto", "pose": [-90, 30, -26, 0, 0, 0, 0.002]},
    
    # --- GRAN TRÁNSITO POR EL AIRE HASTA LOS 90° (Cruza fluido y alto) ---
    {"desc": "6. Viajar alto por el aire de -90° a 90°", "pose": [90, 30, -26, 0, 0, 0, 0.002]},
    
    # --- FASE DE DESCARGA EN 90° ---
    {"desc": "7. Descender sobre la zona de entrega en 90°", "pose": [90, -36, -30, 0, 0, 0, 0.020]},
    {"desc": "8. ¡Abrir Pinza! (Place)", "pose": [90, -36, -30, 0, 0, 0, 0.020]},
    
    # --- RETIRO Y RETORNO ---
    {"desc": "9. Subir y despejar la zona", "pose": [90, 30, -26, 0, 0, 0, 0.002]},
    {"desc": "10. Regresar a Inicio", "pose": [0, 29, -72, 0, 0, 0, 0.020]}
]
# --- 3. CREACIÓN DE LA INTERFAZ GRÁFICA ---
root = tk.Tk()
root.title("Panel Control - Niryo Ned2 FLUIDO")
root.geometry("480x600")
root.configure(bg='#222222')

style = ttk.Style()
style.configure("TLabel", foreground="white", background="#222222", font=("Arial", 11))

title_lbl = ttk.Label(root, text="Niryo Ned2 - Trayectoria Fluida", font=("Arial", 14, "bold"))
title_lbl.pack(pady=15)

status_lbl = ttk.Label(root, text="Estado: Esperando comando...", font=("Arial", 11, "italic"), foreground="#00FF00")
status_lbl.pack(pady=5)

sliders = []
label_values = []

def send_to_txt(*args):
    """Convierte las posiciones actuales a radianes y escribe en el archivo"""
    rad_vals = []
    for i in range(6):
        deg = sliders[i].get()
        label_values[i].config(text=f"{int(deg)}°")
        rad_vals.append(np.radians(deg))
    
    g_val = slider_g.get()
    val_lbl_g.config(text=f"{g_val:.3f}")
    rad_vals.append(g_val)
    
    line = ",".join([f"{x:.6f}" for x in rad_vals])
    try:
        with open(FILENAME, "w") as f:
            f.write(line)
    except Exception as e:
        pass

# --- 4. MOTOR DE INTERPOLACIÓN FLUIDA ---
# Variables de control de trayectoria
paso_secuencia_actual = 0
sub_paso_actual = 0
total_sub_pasos = 60  # Cuantos fragmentos intermedios hay por movimiento (60 pasos = 1.2 segundos fluidos)
pose_inicial_tramo = []

def interpolar_movimiento():
    global sub_paso_actual, paso_secuencia_actual, pose_inicial_tramo
    
    if paso_secuencia_actual >= len(SECUENCIA):
        status_lbl.config(text="Estado: ¡Rutina Pick & Place Finalizada con éxito!", foreground="#00FF00")
        btn_start.config(state="normal")
        return

    pose_objetivo = SECUENCIA[paso_secuencia_actual]["pose"]
    
    # Si estamos empezando un tramo nuevo, guardamos la foto de dónde venía el robot
    if sub_paso_actual == 0:
        pose_inicial_tramo = [sliders[i].get() for i in range(6)] + [slider_g.get()]
        status_lbl.config(text=f"Ejecutando: {SECUENCIA[paso_secuencia_actual]['desc']}", foreground="#FFCC00")

    # Calcular el porcentaje de avance actual (de 0.0 a 1.0)
    t = sub_paso_actual / total_sub_pasos
    
    # Avanzar un milímetro cada articulación
    for i in range(6):
        val_interpolado = pose_inicial_tramo[i] + (pose_objetivo[i] - pose_inicial_tramo[i]) * t
        sliders[i].set(val_interpolado)
        
    val_garra_interpolado = pose_inicial_tramo[6] + (pose_objetivo[6] - pose_inicial_tramo[6]) * t
    slider_g.set(val_garra_interpolado)
    
    # Escribir la coordenada milimétrica en el archivo
    send_to_txt()
    
    sub_paso_actual += 1
    
    if sub_paso_actual <= total_sub_pasos:
        # Repetir este ajuste en 20 milisegundos (Da una tasa de refresco de 50 FPS, ultra fluido)
        root.after(20, interpolar_movimiento)
    else:
        # Tramo terminado, saltamos al siguiente punto clave de la secuencia
        sub_paso_actual = 0
        paso_secuencia_actual += 1
        # Pequeña pausa estática de 400ms al llegar al destino (útil para que la pinza agarre bien)
        root.after(400, interpolar_movimiento)

def comenzar_rutina():
    global paso_secuencia_actual, sub_paso_actual
    btn_start.config(state="disabled")
    paso_secuencia_actual = 0
    sub_paso_actual = 0
    interpolar_movimiento()


# --- 5. ENLACE DE SLIDERS EN LA INTERFAZ ---
joint_names = ["Joint 1", "Joint 2", "Joint 3", "Joint 4", "Joint 5", "Joint 6"]
for i in range(6):
    frame = tk.Frame(root, bg='#222222', pady=5)
    frame.pack(fill='x', padx=20)
    
    lbl = ttk.Label(frame, text=joint_names[i], width=10)
    lbl.pack(side='left')
    
    slider = tk.Scale(frame, from_=JOINT_RANGES[i][0], to=JOINT_RANGES[i][1], orient='horizontal', 
                      bg='#333333', fg='white', highlightbackground='#222222',
                      troughcolor='#555555', command=send_to_txt, resolution=0.1) # Habilitamos decimales para fluidez
    slider.set(SECUENCIA[0]["pose"][i])  
    slider.pack(side='left', fill='x', expand=True, padx=10)
    sliders.append(slider)
    
    val_lbl = ttk.Label(frame, text=f"{SECUENCIA[0]['pose'][i]}°", width=6)
    val_lbl.pack(side='right')
    label_values.append(val_lbl)

# Slider Garra
frame_g = tk.Frame(root, bg='#222222', pady=10)
frame_g.pack(fill='x', padx=20)
lbl_g = ttk.Label(frame_g, text="Garra 1", width=10)
lbl_g.pack(side='left')

slider_g = tk.Scale(frame_g, from_=0.0, to=0.02, resolution=0.0005, orient='horizontal', 
                    bg='#333333', fg='white', highlightbackground='#222222',
                    troughcolor='#555555', command=send_to_txt)
slider_g.set(SECUENCIA[0]["pose"][6])
slider_g.pack(side='left', fill='x', expand=True, padx=10)

val_lbl_g = ttk.Label(frame_g, text=f"{SECUENCIA[0]['pose'][6]:.3f}", width=6)
val_lbl_g.pack(side='right')

# --- 6. BOTÓN RUTA AUTOMÁTICA ---
btn_start = tk.Button(root, text="▶ INICIAR RUTINA FLUIDA", font=("Arial", 12, "bold"),
                      bg="#00AA55", fg="white", activebackground="#008844", activeforeground="white",
                      bd=0, padx=10, pady=10, command=comenzar_rutina)
btn_start.pack(pady=25)

def on_close():
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
send_to_txt()
root.mainloop()