import time
from adafruit_servokit import ServoKit

# ============================================================
# DIAGONAL TROT GAIT (SAFE VERSION)
# ============================================================
# - Uses calibrated neutral angles
# - Opposite corners move together
# - Slow, smooth, conservative motion
# ============================================================

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
# CALIBRATED NEUTRAL ANGLES (FROM YOUR TOOL)
# ------------------------------------------------------------
base_angles = {
    "FL": {"H": 100, "F": 141, "T": 90},
    "FR": {"H": 88,  "F": 47,  "T": 82},
    "BL": {"H": 96,  "F": 133, "T": 85},
    "BR": {"H": 94,  "F": 42,  "T": 91}
}

angles = {
    leg: {joint: base_angles[leg][joint] for joint in base_angles[leg]}
    for leg in base_angles
}

# ------------------------------------------------------------
# APPLY NEUTRAL POSE
# ------------------------------------------------------------
for leg in legs:
    for joint in legs[leg]:
        kit.servo[legs[leg][joint]].angle = angles[leg][joint]

time.sleep(1)

# ------------------------------------------------------------
# GAIT TUNING (SAFE VALUES)
# ------------------------------------------------------------
STEP_FEMUR = 8     # push amount
LIFT_TIBIA = 10    # lift amount
SUBSTEPS   = 10
STEP_TIME  = 0.03

# ------------------------------------------------------------
# SMOOTH MOTION HELPER
# ------------------------------------------------------------
def smooth_move(leg, joint, delta):
    step = delta / SUBSTEPS
    for _ in range(SUBSTEPS):
        angles[leg][joint] += step
        kit.servo[legs[leg][joint]].angle = angles[leg][joint]
        time.sleep(STEP_TIME)

# ------------------------------------------------------------
# LEG ACTIONS
# ------------------------------------------------------------
def lift_leg(leg):
    # tibia flexes → foot up
    smooth_move(leg, "T", -LIFT_TIBIA)

def lower_leg(leg):
    # tibia extends → foot down
    smooth_move(leg, "T", LIFT_TIBIA)

def push_leg(leg):
    # femur swings back → body forward
    smooth_move(leg, "F", STEP_FEMUR)

def reset_femur(leg):
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
        reset_femur(leg)

    time.sleep(0.1)

# ------------------------------------------------------------
# WALK LOOP
# ------------------------------------------------------------
def walk_forward(steps=10):
    for _ in range(steps):
        diagonal_step(
            lift_legs=["FL", "BR"],
            push_legs=["FR", "BL"]
        )

        diagonal_step(
            lift_legs=["FR", "BL"],
            push_legs=["FL", "BR"]
        )

# ------------------------------------------------------------
# RUN
# ------------------------------------------------------------
try:
    walk_forward(steps=20)
except KeyboardInterrupt:
    print("Stopped")
