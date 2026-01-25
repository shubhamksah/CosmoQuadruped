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
PUSH_BACK = 20      # Distance foot moves back on ground
LIFT_TIBIA = 14     # How high the foot lifts
SUB = 10
DT = 0.02

# ------------------------------------------------------------
# MOVE MULTIPLE LEGS IN SYNC
# ------------------------------------------------------------
def move_legs_sync(joint_moves):
    for df, dt, leg in joint_moves:
        angles[leg]["F"] += df
        angles[leg]["T"] += dt
        kit.servo[legs[leg]["F"]].angle = angles[leg]["F"]
        kit.servo[legs[leg]["T"]].angle = angles[leg]["T"]
    time.sleep(DT)

# ------------------------------------------------------------
# DIAGONAL STEP (TRIANGLE PATH)
# ------------------------------------------------------------
def diagonal_step(pair_push, pair_lift):
    # Phase 1: Push-back on ground (considerable distance)
    for _ in range(SUB):
        joint_moves = []
        for leg in pair_push:
            df = FEMUR_SIGN[leg] * (PUSH_BACK / SUB)
            dt = 0  # foot stays low
            joint_moves.append((df, dt, leg))
        for leg in pair_lift:
            df = 0
            dt = TIBIA_SIGN[leg] * (LIFT_TIBIA / SUB)  # lift slightly
            joint_moves.append((df, dt, leg))
        move_legs_sync(joint_moves)

    # Phase 2: Swing forward (lifted leg)
    for _ in range(SUB):
        joint_moves = []
        for leg in pair_lift:
            df = -FEMUR_SIGN[leg] * (PUSH_BACK / SUB)  # forward
            dt = -TIBIA_SIGN[leg] * (LIFT_TIBIA / SUB) # lower foot
            joint_moves.append((df, dt, leg))
        move_legs_sync(joint_moves)

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
