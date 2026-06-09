import mujoco
import mujoco.viewer
import time
import numpy as np
import os
import xml.etree.ElementTree as ET

# Modified XML so that qpos = 0 matches the reference photo posture
robot_xml = ET.tostring(ET.fromstring(open("niryo.xml").read()), encoding="utf8")

FILENAME = "cmd_joints.txt"

# Force the file to initialize at 0 for joints and OPEN (0.020) for the gripper
if not os.path.exists(FILENAME):
    with open(FILENAME, "w") as f:
        f.write("0.0,0.0,0.0,0.0,0.0,0.0,0.020")

model = mujoco.MjModel.from_xml_string(robot_xml)
data = mujoco.MjData(model)

print("-> Starting simulation in MuJoCo.")
print("-> Synchronized with panel BUTTONS (Open = 0.020 / Close = 0.000).")

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
                        # 1. Position the 6 arm joints (indices 0 to 5)
                        data.qpos[:6] = values[:6]
                        
                        # 2. Take the seventh value controlled by the UI panel buttons
                        garra_val = values[6]
                        
                        # Assign the value directly to both gripper fingers in MuJoCo
                        data.qpos[6] = garra_val  # Left finger
                        data.qpos[7] = garra_val  # Right finger
        except Exception:
            pass

        mujoco.mj_step(model, data)
        viewer.sync()
        
        time_until_next_step = model.opt.timestep - (time.time() - step_start)
        if time_until_next_step > 0:
            time.sleep(time_until_next_step)