import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

# -----------------------------
# Servo mapping (anatomical)
# H = Hip, F = Femur, T = Tibia
# -----------------------------
legs = {
    "FL": {"H": 2,  "F": 1,  "T": 0},
    "FR": {"H": 5,  "F": 4,  "T": 3},
    "BL": {"H": 8,  "F": 7,  "T": 6},
    "BR": {"H": 11, "F": 10, "T": 9}
}

# -----------------------------
# Base angles (physically straight)
# -----------------------------
base = {
    "FL": {"H": 100, "F": 141, "T": 90},
    "FR": {"H": 88,  "F": 47,  "T": 82},
    "BL": {"H": 96,  "F": 133, "T": 85},
    "BR": {"H": 94,  "F": 42,  "T": 91}
}

angles = {leg: base[leg].copy() for leg in base}

# -----------------------------
# Safe per-leg parameters (V7)
# -----------------------------
params = {
    "FL": {"TIBIA_LIFT": 18, "FEMUR_SWING": 30, "HIP_SHIFT": 12, "MAX_TIBIA": 110},
    "FR": {"TIBIA_LIFT": 12, "FEMUR_SWING": 25, "HIP_SHIFT": 10, "MAX_TIBIA": 86},
    "BL": {"TIBIA_LIFT": 18, "FEMUR_SWING": 30, "HIP_SHIFT": 12, "MAX_TIBIA": 103},
    "BR": {"TIBIA_LIFT": 12, "FEMUR_SWING": 25, "HIP_SHIFT": 10, "MAX_TIBIA": 105}
}

BODY_LOWER = 2
MICRO_DELAY = 0.015
PHASE_DELAY = 0.25  # slow crawl

# -----------------------------
# Smooth motion helper
# -----------------------------
def move_smooth(leg, joint, target):
    idx = legs[leg][joint]
    current = angles[leg][joint]
    step = 1 if target > current else -1

    for a in range(current, target, step):
        kit.servo[idx].angle = a
        time.sleep(MICRO_DELAY)
    kit.servo[idx].angle = target
    angles[leg][joint] = target

# -----------------------------
# Apply full pose
# -----------------------------
def apply_pose():
    for leg in legs:
        for joint in legs[leg]:
            kit.servo[legs[leg][joint]].angle = angles[leg][joint]
            time.sleep(0.01)

# -----------------------------
# Lower / reset body
# -----------------------------
def lower_body():
    for leg in legs:
        target = max(base[leg]["T"] - BODY_LOWER, 0)
        move_smooth(leg, "T", target)

def reset_body():
    for leg in legs:
        move_smooth(leg, "T", base[leg]["T"])

# -----------------------------
# Shift weight for leg lift
# -----------------------------
def shift_weight(leg):
    direction = params[leg]["HIP_SHIFT"]
    if leg in ["FL", "FR"]:
        move_smooth(leg, "H", base[leg]["H"] + direction)
    else:
        move_smooth(leg, "H", base[leg]["H"] - direction)

def unshift_weight(leg):
    move_smooth(leg, "H", base[leg]["H"])

# -----------------------------
# Lift / lower leg
# -----------------------------
def lift_leg(leg):
    tibia_lift = params[leg]["TIBIA_LIFT"]
    max_tibia = params[leg]["MAX_TIBIA"]
    target = angles[leg]["T"] - tibia_lift
    # Safety clamp to avoid lockout
    target = max(min(target, max_tibia), 0)
    move_smooth(leg, "T", target)

def lower_leg(leg):
    target = max(base[leg]["T"] - BODY_LOWER, 0)
    move_smooth(leg, "T", target)

# -----------------------------
# Swing femur for stepping
# -----------------------------
def swing_leg(leg):
    swing = params[leg]["FEMUR_SWING"]
    if leg in ["FL", "BL"]:
        # Back legs push back, front-left pushes backward slightly for crawl
        move_smooth(leg, "F", base[leg]["F"] - swing)
    else:
        # Front-right and back-right push forward
        move_smooth(leg, "F", base[leg]["F"] + swing)

def reset_femur(leg):
    move_smooth(leg, "F", base[leg]["F"])

# -----------------------------
# Step sequence for one leg
# -----------------------------
def step_leg(leg):
    shift_weight(leg)
    time.sleep(PHASE_DELAY)

    lift_leg(leg)
    time.sleep(PHASE_DELAY)

    swing_leg(leg)
    time.sleep(PHASE_DELAY)

    lower_leg(leg)
    time.sleep(PHASE_DELAY)

    reset_femur(leg)
    time.sleep(PHASE_DELAY)

    unshift_weight(leg)
    time.sleep(PHASE_DELAY)

# -----------------------------
# Crawl gait main loop
# -----------------------------
def crawl_gait():
    print("SAFE TRANSLATING CRAWL GAIT V7 — SLOW AND BALANCED")
    print("Ctrl+C to stop")

    try:
        lower_body()
        time.sleep(1)

        while True:
            # Sequential crawl order for stability
            # FL -> BR -> FR -> BL
            for leg in ["FL", "BR", "FR", "BL"]:
                step_leg(leg)

    except KeyboardInterrupt:
        print("\nStopping safely")
        reset_body()
        apply_pose()

# -----------------------------
# Start program
# -----------------------------
apply_pose()
time.sleep(1)
crawl_gait()
