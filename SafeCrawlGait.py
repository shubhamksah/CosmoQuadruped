import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

# -----------------------------
# Servo mapping
# -----------------------------
legs = {
    "FL": {"H": 2,  "F": 1,  "T": 0},
    "FR": {"H": 5,  "F": 4,  "T": 3},
    "BL": {"H": 8,  "F": 7,  "T": 6},
    "BR": {"H": 11, "F": 10, "T": 9}
}

# -----------------------------
# BASE ANGLES (your calibrated values)
# -----------------------------
base = {
    "FL": {"H": 100, "F": 141, "T": 90},
    "FR": {"H": 88,  "F": 47,  "T": 82},
    "BL": {"H": 96,  "F": 133, "T": 85},
    "BR": {"H": 94,  "F": 42,  "T": 91}
}

angles = {leg: base[leg].copy() for leg in base}

# -----------------------------
# VERY CONSERVATIVE PARAMETERS
# -----------------------------
BODY_LOWER = 4      # lower entire body to reduce torque
TIBIA_LIFT = 4      # tiny lift
FEMUR_STEP = 4      # tiny step
HIP_SHIFT = 3       # tiny weight shift

MICRO_DELAY = 0.03
PHASE_DELAY = 0.5

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
# Apply pose
# -----------------------------
def apply_pose():
    for leg in legs:
        for joint in legs[leg]:
            kit.servo[legs[leg][joint]].angle = angles[leg][joint]
            time.sleep(0.01)

# -----------------------------
# Lower entire robot (safety)
# -----------------------------
def lower_body():
    for leg in legs:
        move_smooth(leg, "T", base[leg]["T"] - BODY_LOWER)

# -----------------------------
# Reset body height
# -----------------------------
def reset_body():
    for leg in legs:
        move_smooth(leg, "T", base[leg]["T"])

# -----------------------------
# Shift weight BEFORE lifting
# -----------------------------
def shift_weight(leg):
    if leg in ["FL", "BL"]:
        move_smooth(leg, "H", base[leg]["H"] + HIP_SHIFT)
    else:
        move_smooth(leg, "H", base[leg]["H"] - HIP_SHIFT)

# -----------------------------
def unshift_weight(leg):
    move_smooth(leg, "H", base[leg]["H"])

# -----------------------------
def lift_leg(leg):
    move_smooth(leg, "T", base[leg]["T"] - BODY_LOWER - TIBIA_LIFT)

# -----------------------------
def lower_leg(leg):
    move_smooth(leg, "T", base[leg]["T"] - BODY_LOWER)

# -----------------------------
def swing_leg(leg):
    if leg in ["FL", "BL"]:
        move_smooth(leg, "F", base[leg]["F"] - FEMUR_STEP)
    else:
        move_smooth(leg, "F", base[leg]["F"] + FEMUR_STEP)

# -----------------------------
def reset_femur(leg):
    move_smooth(leg, "F", base[leg]["F"])

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
def crawl_gait():
    print("SAFE CRAWL GAIT V2")
    print("Ctrl+C to stop")

    try:
        lower_body()
        time.sleep(1)

        while True:
            for leg in ["FL", "BR", "FR", "BL"]:
                step_leg(leg)

    except KeyboardInterrupt:
        print("\nStopping safely")
        reset_body()
        apply_pose()

# -----------------------------
apply_pose()
time.sleep(1)
crawl_gait()
