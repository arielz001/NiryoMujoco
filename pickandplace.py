import tkinter as tk
from tkinter import ttk
import numpy as np

# --- 1. DIGITAL TWIN CONFIGURATION ---
FILENAME = "cmd_joints.txt"

# Joint movement limits (in degrees)
JOINT_RANGES = [
    (-90, 90), (-50, 30), (-50, 120), (-90, 90), (-80, 80), (-50, 50)
]

# --- 2. CORRECTED PICK AND PLACE SEQUENCE (Pick at -90° and Place at 90°) ---
# Pose format: [J1, J2, J3, J4, J5, J6, Gripper]
SECUENCIA = [
    {"desc": "1. Home / Idle Position", "pose": [0, 29, -72, 0, 0, 0, 0.0]},
    
    # --- APPROACH PHASE TO OBJECT AT -90° ---
    {"desc": "2. Rotate to Pick Zone (-90°)", "pose": [-90, 29, -72, 0, 0, 0, 0.0]},
    {"desc": "3. Lower to Find Object at -90°", "pose": [-90, 25, -55, 0, 0, 0, 0.0]},
    {"desc": "4. Close Gripper! (Pick)", "pose": [-90, -22, -50, 0, 0, 0, 0.00]},
    {"desc": "5. Close Gripper! (Pick)", "pose": [-90, -22, -50, 0, 0, 0, 0.02]},
    
    # --- LIFT PHASE (Safety elevation at -90°) ---
    {"desc": "6. Lift Arm Vertically with Object", "pose": [-90, 30, -26, 0, 0, 0, 0.02]},
    
    # --- FLUID AIR TRANSIT TO 90° (Smooth and high cross) ---
    {"desc": "7. Travel High Through Air from -90° to 90°", "pose": [90, 30, -26, 0, 0, 0, 0.02]},
    
    # --- DROP PHASE AT 90° ---
    {"desc": "8. Descend over Delivery Zone at 90°", "pose": [90, -36, -30, 0, 0, 0, 0.02]},
    {"desc": "9. Open Gripper! (Place)", "pose": [90, -36, -30, 0, 0, 0, 0.0]},
    
    # --- RETRACT AND RETURN ---
    {"desc": "10. Raise and Clear Zone", "pose": [90, 30, -26, 0, 0, 0, 0.0]},
    {"desc": "11. Return Home", "pose": [0, 29, -72, 0, 0, 0, 0.0]}
]

# --- 3. GUI CREATION ---
root = tk.Tk()
root.title("Control Panel - Niryo Ned2 SMOOTH")
root.geometry("480x600")
root.configure(bg='#222222')

style = ttk.Style()
style.configure("TLabel", foreground="white", background="#222222", font=("Arial", 11))

title_lbl = ttk.Label(root, text="Niryo Ned2 - Smooth Trajectory", font=("Arial", 14, "bold"))
title_lbl.pack(pady=15)

status_lbl = ttk.Label(root, text="Status: Waiting for command...", font=("Arial", 11, "italic"), foreground="#00FF00")
status_lbl.pack(pady=5)

sliders = []
label_values = []

def send_to_txt(*args):
    """Convert current positions to radians and write to file"""
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

# --- 4. SMOOTH INTERPOLATION ENGINE ---
# Trajectory control variables
paso_secuencia_actual = 0
sub_paso_actual = 0
total_sub_pasos = 60  # Intermediate steps per movement (60 steps = 1.2 smooth seconds)
pose_inicial_tramo = []

def interpolar_movimiento():
    global sub_paso_actual, paso_secuencia_actual, pose_inicial_tramo
    
    if paso_secuencia_actual >= len(SECUENCIA):
        status_lbl.config(text="Status: Pick & Place Routine Completed Successfully!", foreground="#00FF00")
        btn_start.config(state="normal")
        return

    pose_objetivo = SECUENCIA[paso_secuencia_actual]["pose"]
    
    # Store initial state when starting a new segment
    if sub_paso_actual == 0:
        pose_inicial_tramo = [sliders[i].get() for i in range(6)] + [slider_g.get()]
        status_lbl.config(text=f"Executing: {SECUENCIA[paso_secuencia_actual]['desc']}", foreground="#FFCC00")

    # Calculate current progress percentage (0.0 to 1.0)
    t = sub_paso_actual / total_sub_pasos
    
    # Step each joint slightly
    for i in range(6):
        val_interpolado = pose_inicial_tramo[i] + (pose_objetivo[i] - pose_inicial_tramo[i]) * t
        sliders[i].set(val_interpolado)
        
    val_garra_interpolado = pose_inicial_tramo[6] + (pose_objetivo[6] - pose_inicial_tramo[6]) * t
    slider_g.set(val_garra_interpolado)
    
    # Write coordinates to file
    send_to_txt()
    
    sub_paso_actual += 1
    
    if sub_paso_actual <= total_sub_pasos:
        # Refresh in 20 milliseconds (50 FPS refresh rate, ultra smooth)
        root.after(20, interpolar_movimiento)
    else:
        # Segment finished, advance to next keypoint
        sub_paso_actual = 0
        paso_secuencia_actual += 1
        # Short 400ms static pause at destination for stable grip/release
        root.after(400, interpolar_movimiento)

def comenzar_rutina():
    global paso_secuencia_actual, sub_paso_actual
    btn_start.config(state="disabled")
    paso_secuencia_actual = 0
    sub_paso_actual = 0
    interpolar_movimiento()


# --- 5. BIND SLIDERS IN THE INTERFACE ---
joint_names = ["Joint 1", "Joint 2", "Joint 3", "Joint 4", "Joint 5", "Joint 6"]
for i in range(6):
    frame = tk.Frame(root, bg='#222222', pady=5)
    frame.pack(fill='x', padx=20)
    
    lbl = ttk.Label(frame, text=joint_names[i], width=10)
    lbl.pack(side='left')
    
    slider = tk.Scale(frame, from_=JOINT_RANGES[i][0], to=JOINT_RANGES[i][1], orient='horizontal', 
                      bg='#333333', fg='white', highlightbackground='#222222',
                      troughcolor='#555555', command=send_to_txt, resolution=0.1) # Enable decimals for smoothness
    slider.set(SECUENCIA[0]["pose"][i])  
    slider.pack(side='left', fill='x', expand=True, padx=10)
    sliders.append(slider)
    
    val_lbl = ttk.Label(frame, text=f"{SECUENCIA[0]['pose'][i]}°", width=6)
    val_lbl.pack(side='right')
    label_values.append(val_lbl)

# Gripper Slider
frame_g = tk.Frame(root, bg='#222222', pady=10)
frame_g.pack(fill='x', padx=20)
lbl_g = ttk.Label(frame_g, text="Gripper 1", width=10)
lbl_g.pack(side='left')

slider_g = tk.Scale(frame_g, from_=0.0, to=0.02, resolution=0.0005, orient='horizontal', 
                    bg='#333333', fg='white', highlightbackground='#222222',
                    troughcolor='#555555', command=send_to_txt)
slider_g.set(SECUENCIA[0]["pose"][6])
slider_g.pack(side='left', fill='x', expand=True, padx=10)

val_lbl_g = ttk.Label(frame_g, text=f"{SECUENCIA[0]['pose'][6]:.3f}", width=6)
val_lbl_g.pack(side='right')

# --- 6. AUTOMATIC ROUTINE BUTTON ---
btn_start = tk.Button(root, text="▶ START SMOOTH ROUTINE", font=("Arial", 12, "bold"),
                      bg="#00AA55", fg="white", activebackground="#008844", activeforeground="white",
                      bd=0, padx=10, pady=10, command=comenzar_rutina)
btn_start.pack(pady=25)

def on_close():
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
send_to_txt()
root.mainloop()