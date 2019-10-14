import rtde_control

rtde_c = rtde_control.RTDEControlInterface("127.0.0.1")
velocity = 0.8
acceleration = 1.2
blend1 = 0
blend2 = 0.3
blend3 = 0
pose1 = [-1.6, -1.8, -2.09, -0.844, 1.59, -0.0255, velocity, acceleration, blend1]
pose2 = [-0.738, -1.99, -1.83, -0.894, 1.60, 0.827, velocity, acceleration, blend2]
pose3 = [-1.6, -1.63, -1.07, -2.03, 1.59, -0.0202, velocity, acceleration, blend3]

path = [pose1, pose2, pose3]

rtde_c.moveJ(path)
