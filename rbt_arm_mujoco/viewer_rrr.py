import mujoco
import mujoco.viewer
import numpy as np

model = mujoco.MjModel.from_xml_path("rrr.xml")
data = mujoco.MjData(model)

t = 0
speed = 0.0001
with mujoco.viewer.launch_passive(model, data) as viewer:
    while viewer.is_running():
        # base yaw
        data.ctrl[0] = 0.5 * np.sin(t)

        # shoulder
        data.ctrl[1] = 0.5 * np.sin(speed * t)

        # elbow
        data.ctrl[2] = 0.5 * np.cos(speed * t)

        mujoco.mj_step(model, data)

        viewer.sync()

        t += 0.01
