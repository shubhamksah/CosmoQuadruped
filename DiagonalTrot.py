import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

# ------------------------------------------------------------
# SERVO MAP
# ------------------------------------------------------------
legs = {
    "FL": {"H": 2,  "F": 1,  "T": 0},
    "FR": {"H": 5,  "F": 4,  "T": 3},
    "BL": {"H": 8,  "F": 7,  "T": 6},
    "BR": {"H": 11, "F": 10, "T": 9}
}

# ------------------------------------------------------------
# BASE ANGLES
# ------------------------------------------------------------
base = {
    "FL": {"H": 100, "F": 141, "T": 132},
    "FR": {"H": 88,  "F": 47,  "T": 40},
    "BL": {"H": 96,  "F": 133, "T": 127},
    "BR": {"H": 94,  "F": 42,  "T": 49}
}

angles = {leg: base[leg].copy() for leg in base}

# ------------------------------------------------------------
# APPLY NEUTRAL
# ------------------------------------------------------------
for leg in legs:
    for j in legs[leg]:
        kit.servo[legs[leg][j]].angle = angles[leg][j]

time.sleep(1)

# ------------------------------------------------------------
# SIGN MAPS
# ------------------------------------------------------------
FEMUR_SIGN = {"FL": +1, "BL": +1, "FR": -1, "BR": -1}
TIBIA_SIGN = {"FL": -1, "BL": -1, "FR": +1, "BR": +1}

# ------------------------------------------------------------
# GAIT PARAMETERS
# ------------------------------------------------------------
FEMUR_PUSH = 18
TIBIA_COMP = 0.6
LIFT_TIBIA = 14

SUB = 10
DT = 0.025

# ------------------------------------------------------------
# SYNC JOINT MOVEMENT
# ------------------------------------------------------------
def move_joints_sync(joint_moves, steps=SUB, dt=DT):
    step_deltas = [(leg, joint, delta / steps) for leg, joint, delta in joint_moves]
    for _ in range(steps):
        for leg, joint, step in step_deltas:
            angles[leg][joint] += step
            kit.servo[legs[leg][joint]].angle = angles[leg][joint]
        time.sleep(dt)

# ------------------------------------------------------------
# FOOT PUSH ON GROUND
# ------------------------------------------------------------
def push_legs(legs_to_push):
    joint_moves = []
    for leg in legs_to_push:
        df = FEMUR_SIGN[leg] * FEMUR_PUSH
        dt = TIBIA_SIGN[leg] * (-TIBIA_COMP * FEMUR_PUSH)
        joint_moves.append((leg, "F", df))
        joint_moves.append((leg, "T", dt))
    move_joints_sync(joint_moves)

# ------------------------------------------------------------
# LIFT, DROP, RETURN
# ------------------------------------------------------------
def lift_legs(legs_to_lift):
    joint_moves = [(leg, "T", TIBIA_SIGN[leg] * LIFT_TIBIA) for leg in legs_to_lift]
    move_joints_sync(joint_moves)

def drop_legs(legs_to_lift):
    joint_moves = [(leg, "T", -TIBIA_SIGN[leg] * LIFT_TIBIA) for leg in legs_to_lift]
    move_joints_sync(joint_moves)

def return_legs(legs_to_lift):
    joint_moves = []
    for leg in legs_to_lift:
        df = -FEMUR_SIGN[leg] * FEMUR_PUSH
        dt = TIBIA_SIGN[leg] * (TIBIA_COMP * FEMUR_PUSH)
        joint_moves.append((leg, "F", df))
        joint_moves.append((leg, "T", dt))
    move_joints_sync(joint_moves)

# ------------------------------------------------------------
# DIAGONAL STEP
# ------------------------------------------------------------
def diagonal_step(pair_push, pair_lift):
    lift_legs(pair_lift)
    push_legs(pair_push)
    drop_legs(pair_lift)
    return_legs(pair_lift)

# ------------------------------------------------------------
# WALK FUNCTION
# ------------------------------------------------------------
def walk(steps=6):
    for _ in range(steps):
        diagonal_step(["FR", "BL"], ["FL", "BR"])
        diagonal_step(["FL", "BR"], ["FR", "BL"])

# ------------------------------------------------------------
# RUN
# ------------------------------------------------------------
try:
    walk(steps=10)
except KeyboardInterrupt:
    print("Stopped")
