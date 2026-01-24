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
# Base angles (calibrated for straight pose)
# -----------------------------
base = {
    "FL": {"H": 100, "F": 141, "T": 90},  # FL: hip clockwise+, femur back+, tibia down+ = standing taller
    "FR": {"H": 88,  "F": 47,  "T": 82},  # FR: hip clockwise+, femur forward+, tibia up+
    "BL": {"H": 96,  "F": 133, "T": 85},  # BL: hip counter+, femur back+, tibia down+
    "BR": {"H": 94,  "F": 42,  "T": 91}   # BR: hip counter+, femur forward+, tibia up+
}

angles = {leg: base[leg].copy() for leg in base}

# -----------------------------
# SAFE PARAMETERS (V4)
# -----------------------------
BODY_LOWER = 4      # lowers body slightly for less torque
TIBIA_LIFT = 12     # slightly bigger lift to start translating forward
FEMUR_STEP = 12     # slightly bigger swing to push forward
HIP_SHIFT = 7       # bigger shift to unload leg

MICRO_DELAY = 0.02
PHASE_DELAY = 0.3   # slightly faster for forward motion

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
# Lower entire robot safely
# -----------------------------
def lower_body():
    for leg in legs:
        move_smooth(leg, "T", base[leg]["T"] - BODY_LOWER)

def reset_body():
    for leg in legs:
        move_smooth(leg, "T", base[leg]["T"])

# -----------------------------
# Shift weight for leg lift
# -----------------------------
def shift_weight(leg):
    if leg in ["FL", "BL"]:
        move_smooth(leg, "H", base[leg]["H"] + HIP_SHIFT)
    else:
        move_smooth(leg, "H", base[leg]["H"] - HIP_SHIFT)

def unshift_weight(leg):
    move_smooth(leg, "H", base[leg]["H"])

# -----------------------------
# Lift / lower leg
# -----------------------------
def lift_leg(leg):
    move_smooth(leg, "T", base[leg]["T"] - BODY_LOWER - TIBIA_LIFT)

def lower_leg(leg):
    move_smooth(leg, "T", base[leg]["T"] - BODY_LOWER)

# -----------------------------
# Swing femur for stepping
# -----------------------------
def swing_leg(leg):
    if leg in ["FL", "BL"]:
        move_smooth(leg, "F", base[leg]["F"] - FEMUR_STEP)  # back
    else:
        move_smooth(leg, "F", base[leg]["F"] + FEMUR_STEP)  # forward

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
# Main crawl gait
# -----------------------------
def crawl_gait():
    print("SAFE FORWARD CRAWL GAIT V4 — SLOW AND STABLE")
    print("Ctrl+C to stop")

    try:
        lower_body()
        time.sleep(1)

        while True:
            # Order chosen for maximum stability:
            # Front-left → Back-right → Front-right → Back-left
            for leg in ["FL", "BR", "FR", "BL"]:
                step_leg(leg)

    except KeyboardInterrupt:
        print("\nStopping safely")
        reset_body()
        apply_pose()

# -----------------------------
# Start
# -----------------------------
apply_pose()
time.sleep(1)
crawl_gait()
