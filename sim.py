import mujoco
import mujoco.viewer
import time
import numpy as np
import os

# XML modificado para que qpos = 0 coincida con la postura de la foto
robot_xml = """
<mujoco model="niryo_ned2_con_garra">
    <compiler angle="radian" coordinate="local"/>
    <option gravity="0 0 0"/>

    <asset>
        <texture name="grid" type="2d" builtin="checker" rgb1=".1 .2 .3" rgb2=".2 .3 .4" width="512" height="512"/>
        <material name="grid" texture="grid" texrepeat="1 1" texuniform="true"/>
    </asset>

    <worldbody>
        <light pos="0 0 3" dir="0 0 -1" directional="true"/>
        <geom name="floor" size="0 0 .05" type="plane" material="grid"/>

        <body name="base_link" pos="0 0 0">
            <geom name="base_geom" type="cylinder" size="0.08 0.05" pos="0 0 0.05" rgba="0.1 0.5 0.8 1"/>
            
            <body name="shoulder_link" pos="0 0 0.103">
                <joint name="joint_1" type="hinge" axis="0 0 1" range="-2.949 2.949"/>
                <geom type="cylinder" size="0.05 0.04" pos="0 0 0.04" rgba="0.2 0.2 0.2 1"/>
                
                <body name="arm_link" pos="0 0 0.08">
                    <joint name="joint_2" type="hinge" axis="0 -1 0" range="-1.83 0.61"/>
                    <geom type="capsule" size="0.035" fromto="0 0 0 0 0 0.221" rgba="0.1 0.5 0.8 1"/>
                    
                    <body name="forearm_link" pos="0 0 0.221">
                        <joint name="joint_3" type="hinge" axis="0 -1 0" range="-2.68 3.14"/>
                        <geom type="capsule" size="0.03" fromto="0 0 0 0.201 0 0" rgba="0.2 0.2 0.2 1"/>
                        
                        <body name="wrist_link" pos="0.201 0 0">
                            <joint name="joint_4" type="hinge" axis="1 0 0" range="-2.089 2.089"/>
                            <geom type="capsule" size="0.025" fromto="0 0 0 0.06 0 0" rgba="0.1 0.5 0.8 1"/>
                            
                            <body name="wrist_flex_link" pos="0.06 0 0">
                                <joint name="joint_5" type="hinge" axis="0 -1 0" range="-1.919 1.922"/>
                                <geom type="cylinder" size="0.025 0.015" quat="0.7071 0 0.7071 0" rgba="0.2 0.2 0.2 1"/>
                                
                                <body name="tool_link" pos="0.04 0 0">
                                    <joint name="joint_6" type="hinge" axis="1 0 0" range="-2.53 2.53"/>
                                    <geom type="box" size="0.015 0.035 0.02" rgba="0.1 0.1 0.1 1"/>
                                    
                                    <body name="left_finger" pos="0.015 0.025 0">
                                        <joint name="joint_base_to_left_finger" type="slide" axis="0 -1 0" range="0 0.02"/>
                                        <geom type="box" size="0.02 0.005 0.01" pos="0.01 0 0" rgba="0.9 0.1 0.1 1"/>
                                    </body>

                                    <body name="right_finger" pos="0.015 -0.025 0">
                                        <joint name="joint_base_to_right_finger" type="slide" axis="0 1 0" range="0 0.02"/>
                                        <geom type="box" size="0.02 0.005 0.01" pos="0.01 0 0" rgba="0.9 0.1 0.1 1"/>
                                    </body>
                                </body>
                            </body>
                        </body>
                    </body>
                </body>
            </body>
        </body>
    </worldbody>
</mujoco>
"""

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