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
# YOUR BASE ANGLES
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
# SIGN MAPS (CRITICAL)
# ------------------------------------------------------------
FEMUR_SIGN = {
    "FL": +1, "BL": +1,
    "FR": -1, "BR": -1
}

TIBIA_SIGN = {
    "FL": -1, "BL": -1,
    "FR": +1, "BR": +1
}

# ------------------------------------------------------------
# GAIT PARAMETERS (REAL MOTION)
# ------------------------------------------------------------
FEMUR_PUSH = 18      # THIS is what moves the robot
TIBIA_COMP = 0.6     # poor-man’s IK ratio
LIFT_TIBIA = 14

SUB = 10
DT = 0.025

# ------------------------------------------------------------
def move_joint(leg, joint, delta):
    step = delta / SUB
    for _ in range(SUB):
        angles[leg][joint] += step
        kit.servo[legs[leg][joint]].angle = angles[leg][joint]
        time.sleep(DT)

# ------------------------------------------------------------
# FOOT STRAIGHT BACK (ON GROUND)
# ------------------------------------------------------------
def push_leg(leg):
    df = FEMUR_SIGN[leg] * FEMUR_PUSH
    dt = TIBIA_SIGN[leg] * (-TIBIA_COMP * FEMUR_PUSH)

    move_joint(leg, "F", df)
    move_joint(leg, "T", dt)

# ------------------------------------------------------------
# FOOT LIFT + RETURN
# ------------------------------------------------------------
def lift_leg(leg):
    move_joint(leg, "T", TIBIA_SIGN[leg] * LIFT_TIBIA)

def drop_leg(leg):
    move_joint(leg, "T", -TIBIA_SIGN[leg] * LIFT_TIBIA)

def return_leg(leg):
    df = -FEMUR_SIGN[leg] * FEMUR_PUSH
    dt = TIBIA_SIGN[leg] * (TIBIA_COMP * FEMUR_PUSH)

    move_joint(leg, "F", df)
    move_joint(leg, "T", dt)

# ------------------------------------------------------------
# DIAGONAL STEP — PERFECT SYNC
# ------------------------------------------------------------
def diagonal_step(pair_push, pair_lift):
    # Lift diagonal
    for leg in pair_lift:
        lift_leg(leg)

    # Push grounded diagonal (IN SYNC)
    for leg in pair_push:
        push_leg(leg)

    # Drop lifted legs
    for leg in pair_lift:
        drop_leg(leg)

    # Return lifted legs forward
    for leg in pair_lift:
        return_leg(leg)

# ------------------------------------------------------------
def walk(steps=6):
    for _ in range(steps):
        diagonal_step(["FR", "BL"], ["FL", "BR"])
        diagonal_step(["FL", "BR"], ["FR", "BL"])

# ------------------------------------------------------------
try:
    walk(steps=10)
except KeyboardInterrupt:
    print("Stopped")
