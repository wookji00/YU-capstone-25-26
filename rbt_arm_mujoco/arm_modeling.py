import mujoco

spec = mujoco.MjSpec()

# 바닥 고정: 오직 z축 기준 rotate
base = spec.worldbody.add_body(
    name="base",  # 링크의 이름
    pos=[0, 0, 0],  # list로 좌표값을 넣는다
)

link1 = (
    base.add_body(  # spec.add_body 가 아니라 기준이 되는 링크로부터 나온다고 가정해야함
        # 즉 base.add_body가 되어야한다
        name="link_1",
        pos=[0, 0, 10],
    )
)

link2 = link1.add_body(  # 그럼 얘도 link1.add_body가 되어야 링크 양끝에 base, link2가 있겠네.
    name="link_2", pos=[0, 0, 20]
)

link3 = link2.add_body(name="link_3", pos=[0, 0, 10])


pin1 = link1.add_joint(
    type=mujoco.mjtJoint.mjJNT_HINGE,
    axis=[0, 0, 1],  # 이러면 z축 기준 rotate인가?
)

pin2 = link2.add_joint(
    type=mujoco.mjtJoint.mjJNT_HINGE,
    axis=[0, 1, 0],  # 이러면 y축 기준 rotate인가?
)

pin3 = link3.add_joint(
    type=mujoco.mjtJoint.mjJNT_HINGE,
    axis=[0, 1, 0],  # 이러면 y축 기준 rotate인가?
)

link1.add_geom(
    type=mujoco.mjtGeom.mjGEOM_CAPSULE, fromto=[0, 0, 0, 0, 0, 10], size=[0.1]
)

link2.add_geom(
    type=mujoco.mjtGeom.mjGEOM_CAPSULE, fromto=[0, 0, 0, 0, 0, 20], size=[0.1]
)

link3.add_geom(
    type=mujoco.mjtGeom.mjGEOM_CAPSULE, fromto=[0, 0, 0, 0, 0, 10], size=[0.1]
)

servo1 = spec.add_actuator(target=pin1.name, trntype=0)

servo2 = spec.add_actuator(target=pin2.name, trntype=0)

servo3 = spec.add_actuator(target=pin2.name, trntype=0)

model = spec.compile()
# print(spec.to_xml())
spec.encode("model.xml", model)

data = mujoco.MjData(model)

with mujoco.viewer.launch_passive(model, data) as viewer:
    while viewer.is_running():
        data.ctrl[0] = 0.3

        mujoco.mj_step(model, data)

        viewer.sync()
