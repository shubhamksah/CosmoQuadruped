import time
from adafruit_servokit import ServoKit

# ============================================================
# ULTRA-SAFE QUADRUPED CRAWL GAIT
#
# GOALS:
# - Minimal speed
# - One leg moves at a time
# - 3 legs always on ground
# - No sudden angle changes
#
# THIS IS A SAFETY-FIRST GAIT
# ============================================================

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
# BASE (CALIBRATED) ANGLES
# MUST MATCH YOUR TWEAKER OUTPUT
# -----------------------------
base = {
    "FL": {"H": 100, "F": 141, "T": 90},
    "FR": {"H": 88,  "F": 47,  "T": 82},
    "BL": {"H": 96,  "F": 133, "T": 85},
    "BR": {"H": 94,  "F": 42,  "T": 91}
}

# Copy base into live state
angles = {leg: base[leg].copy() for leg in base}

# -----------------------------
# SAFETY LIMITS
# -----------------------------
TIBIA_LIFT = 8      # degrees to lift foot (SMALL)
FEMUR_STEP = 6     # degrees forward step (SMALL)
STEP_DELAY = 0.35  # seconds (SLOW)
MICRO_DELAY = 0.02 # smooth servo motion

# -----------------------------
# Apply initial pose
# -----------------------------
def apply_pose():
    for leg in legs:
        for joint in legs[leg]:
            kit.servo[legs[leg][joint]].angle = angles[leg][joint]
            time.sleep(MICRO_DELAY)

# -----------------------------
# Move a servo smoothly
# -----------------------------
def move_smooth(leg, joint, target):
    idx = legs[leg][joint]
    current = angles[leg][joint]

    step = 1 if target > current else -1
    for angle in range(current, target, step):
        kit.servo[idx].angle = angle
        time.sleep(MICRO_DELAY)

    angles[leg][joint] = target
    kit.servo[idx].angle = target

# -----------------------------
# Lift leg (tibia compress)
# -----------------------------
def lift_leg(leg):
    move_smooth(leg, "T", base[leg]["T"] - TIBIA_LIFT)

# -----------------------------
# Lower leg (tibia extend)
# -----------------------------
def lower_leg(leg):
    move_smooth(leg, "T", base[leg]["T"])

# -----------------------------
# Swing leg forward
# -----------------------------
def swing_leg_forward(leg):
    if leg in ["FL", "BL"]:
        target = base[leg]["F"] - FEMUR_STEP
    else:
        target = base[leg]["F"] + FEMUR_STEP

    move_smooth(leg, "F", target)

# -----------------------------
# Return femur to neutral
# -----------------------------
def reset_femur(leg):
    move_smooth(leg, "F", base[leg]["F"])

# -----------------------------
# ONE SAFE STEP
# -----------------------------
def step_leg(leg):
    lift_leg(leg)
    time.sleep(STEP_DELAY)

    swing_leg_forward(leg)
    time.sleep(STEP_DELAY)

    lower_leg(leg)
    time.sleep(STEP_DELAY)

    reset_femur(leg)
    time.sleep(STEP_DELAY)

# -----------------------------
# MAIN GAIT LOOP
# -----------------------------
def crawl_gait():
    print("Starting SAFE crawl gait")
    print("Ctrl+C to stop")

    try:
        while True:
            for leg in ["FL", "BR", "FR", "BL"]:
                step_leg(leg)

    except KeyboardInterrupt:
        print("\nStopping safely")
        apply_pose()

# -----------------------------
# START
# -----------------------------
apply_pose()
time.sleep(1)
crawl_gait()
