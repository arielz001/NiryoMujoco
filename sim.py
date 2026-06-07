import mujoco
import mujoco.viewer
import time
import numpy as np
import os
import xml.etree.ElementTree as ET
# XML modificado para que qpos = 0 coincida con la postura de la foto
robot_xml = ET.tostring(ET.fromstring(open("niryo.xml").read()), encoding="utf8")

FILENAME = "cmd_joints.txt"

# Forzar a que el archivo inicialice en 0 para comprobar la postura
if not os.path.exists(FILENAME):
    with open(FILENAME, "w") as f:
        f.write("0.0,0.0,0.0,0.0,0.0,0.0,0.010")

model = mujoco.MjModel.from_xml_string(robot_xml)
data = mujoco.MjData(model)

print("-> Iniciando simulación. Modifica 'cmd_joints.txt' con ceros para ver la posición fija.")

with mujoco.viewer.launch_passive(model, data) as viewer:
    viewer.cam.distance = 1.3
    viewer.cam.lookat = [0.2, 0, 0.25]
    viewer.cam.elevation = -20
    viewer.cam.azimuth = 135
    
    while viewer.is_running():
        step_start = time.time()
        
        try:
            with open(FILENAME, "r") as f:
                line = f.read().strip()
                if line:
                    values = [float(x) for x in line.split(",")]
                    if len(values) == 7:
                        data.qpos[:6] = values[:6]
                        data.qpos[6] = values[6]
                        data.qpos[7] = values[6]
        except Exception:
            pass

        mujoco.mj_step(model, data)
        viewer.sync()
        
        time_until_next_step = model.opt.timestep - (time.time() - step_start)
        if time_until_next_step > 0:
            time.sleep(time_until_next_step)