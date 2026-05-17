import mujoco
import mujoco.viewer
import numpy as np

model = mujoco.MjModel.from_xml_path("arm.xml")
data = mujoco.MjData(model)

with mujoco.viewer.launch_passive(model, data) as viewer:
    t = 0
    a = 0.2

    while viewer.is_running():
        data.ctrl[0] = np.sin(a * t)
        data.ctrl[1] = 0.5 * np.sin(a * t)
        data.ctrl[2] = 0.3 * np.cos(a * t)

        mujoco.mj_step(model, data)

        viewer.sync()

        t += 0.00
