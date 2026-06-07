from pyniryo import *
import tkinter as tk
import math
import os

# Configuración del archivo de comunicación con MuJoCo
FILENAME = "cmd_joints.txt"

# Conexión con el robot real
robot = NiryoRobot("10.10.10.10")
robot.calibrate_auto()
robot.update_tool()
robot.release_with_tool()

current = robot.get_joints()

# Límites de los joints en grados
limits_deg = [
    (-90, 90),   # J1
    (-50, 30),   # J2
    (-120, 120), # J3
    (-90, 90),   # J4
    (-80, 80),   # J5
    (-100, 100)  # J6
]

root = tk.Tk()
root.title("Ned2 Joint Control + MuJoCo Sync")

sliders = []

for i in range(6):
    frame = tk.Frame(root)
    frame.pack(fill="x", padx=10, pady=5)

    tk.Label(frame, text=f"Joint {i+1}").pack(side="left")

    slider = tk.Scale(
        frame,
        from_=limits_deg[i][0],
        to=limits_deg[i][1],
        orient="horizontal",
        length=500,
        resolution=1
    )

    slider.set(math.degrees(current[i]))
    slider.pack(side="left")
    sliders.append(slider)

def move_robot():
    # 1. Obtener los joints en radianes desde los sliders
    joints = [math.radians(slider.get()) for slider in sliders]

    try:
        # 2. Mover el robot físico real
        robot.move_joints(joints)
        print("Robot real movido a:", joints)
        
        # 3. GUARDAR EN EL ARCHIVO PARA MUJOCO
        # MuJoCo espera 7 valores (6 joints + 1 para la apertura de la garra)
        # Añadimos un valor fijo de 0.010 para mantener la garra medio abierta en el simulador
        joints_str = ",".join([f"{j:.6f}" for j in joints]) + ",0.010"
        
        with open(FILENAME, "w") as f:
            f.write(joints_str)
        print(f"Sincronizado con MuJoCo -> Guardado en {FILENAME}")

    except Exception as e:
        print("Error al mover o guardar:", e)

def refresh():
    joints = robot.get_joints()
    print(f"Actual joints robot real: {joints}")
    for i in range(6):
        sliders[i].set(math.degrees(joints[i]))
        
    # También actualizamos el archivo al leer la posición actual
    joints_str = ",".join([f"{j:.6f}" for j in joints]) + ",0.010"
    with open(FILENAME, "w") as f:
        f.write(joints_str)

tk.Button(root, text="Move", command=move_robot).pack(pady=10)
tk.Button(root, text="Read Current Pose", command=refresh).pack(pady=5)

def on_close():
    robot.close_connection()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()