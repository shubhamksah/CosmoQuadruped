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
# NEW CALIBRATED BASE ANGLES (YOUR VALUES)
# ------------------------------------------------------------
base_angles = {
    "FL": {"H": 100, "F": 141, "T": 132},
    "FR": {"H": 88,  "F": 47,  "T": 40},
    "BL": {"H": 96,  "F": 133, "T": 127},
    "BR": {"H": 94,  "F": 42,  "T": 49}
}

angles = {
    leg: {j: base_angles[leg][j] for j in base_angles[leg]}
    for leg in base_angles
}

# ------------------------------------------------------------
# APPLY NEUTRAL
# ------------------------------------------------------------
for leg in legs:
    for joint in legs[leg]:
        kit.servo[legs[leg][joint]].angle = angles[leg][joint]

time.sleep(1)

# ------------------------------------------------------------
# TIBIA DIRECTION MAP (THIS FIXES EVERYTHING)
# ------------------------------------------------------------
TIBIA_LIFT_SIGN = {
    "FL": -1,
    "BL": -1,
    "FR": +1,
    "BR": +1
}

# ------------------------------------------------------------
# SAFE GAIT PARAMETERS
# ------------------------------------------------------------
STEP_FEMUR = 6     # push amount
LIFT_TIBIA = 7     # lift amount (small on purpose)
SUBSTEPS   = 12
DT         = 0.03

# ------------------------------------------------------------
# SMOOTH MOVE
# ------------------------------------------------------------
def smooth_move(leg, joint, delta):
    step = delta / SUBSTEPS
    for _ in range(SUBSTEPS):
        angles[leg][joint] += step
        kit.servo[legs[leg][joint]].angle = angles[leg][joint]
        time.sleep(DT)

# ------------------------------------------------------------
# LEG ACTIONS
# ------------------------------------------------------------
def lift_leg(leg):
    smooth_move(
        leg,
        "T",
        TIBIA_LIFT_SIGN[leg] * LIFT_TIBIA
    )

def lower_leg(leg):
    smooth_move(
        leg,
        "T",
        -TIBIA_LIFT_SIGN[leg] * LIFT_TIBIA
    )

def push_leg(leg):
    smooth_move(leg, "F", STEP_FEMUR)

def reset_leg(leg):
    smooth_move(leg, "F", -STEP_FEMUR)

# ------------------------------------------------------------
# DIAGONAL STEP
# ------------------------------------------------------------
def diagonal_step(lift_legs, push_legs):
    for leg in lift_legs:
        lift_leg(leg)

    time.sleep(0.05)

    for leg in push_legs:
        push_leg(leg)

    time.sleep(0.05)

    for leg in lift_legs:
        lower_leg(leg)

    time.sleep(0.05)

    for leg in push_legs:
        reset_leg(leg)

    time.sleep(0.1)

# ------------------------------------------------------------
# WALK LOOP
# ------------------------------------------------------------
def walk_forward(steps=10):
    for _ in range(steps):
        diagonal_step(["FL", "BR"], ["FR", "BL"])
        diagonal_step(["FR", "BL"], ["FL", "BR"])

# ------------------------------------------------------------
# RUN
# ------------------------------------------------------------
try:
    walk_forward(steps=20)
except KeyboardInterrupt:
    print("Stopped safely")
