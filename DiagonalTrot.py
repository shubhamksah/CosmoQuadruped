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
FEMUR_PUSH = 18      # push back distance
LIFT_TIBIA = 14      # leg lift height
SUB = 10
DT = 0.02

# ------------------------------------------------------------
# KINEMATICS-LIKE FOOT CONTROL
# ------------------------------------------------------------
def move_leg_path(leg, path_points):
    """
    Move a leg along a path in small increments.
    path_points: list of tuples (delta_femur, delta_tibia)
    """
    for df, dt in path_points:
        angles[leg]["F"] += df
        angles[leg]["T"] += dt
        kit.servo[legs[leg]["F"]].angle = angles[leg]["F"]
        kit.servo[legs[leg]["T"]].angle = angles[leg]["T"]
        time.sleep(DT)

# ------------------------------------------------------------
# DEFINE TRIANGLE PATH
# ------------------------------------------------------------
def triangle_leg_motion(leg):
    """
    Moves leg in a triangle pattern:
    1. Stance (down)
    2. Push back (foot stays low, maybe slightly down)
    3. Lift + swing forward
    """
    # Divide each movement into SUB steps
    df_push = FEMUR_SIGN[leg] * FEMUR_PUSH / SUB
    dt_push = TIBIA_SIGN[leg] * 0  # stay flat (no lift)
    
    df_swing = -FEMUR_SIGN[leg] * FEMUR_PUSH / SUB
    dt_swing = TIBIA_SIGN[leg] * LIFT_TIBIA / SUB

    # 1. Push back
    push_path = [(df_push, dt_push) for _ in range(SUB)]
    move_leg_path(leg, push_path)

    # 2. Lift & swing forward
    swing_path = [(df_swing, dt_swing) for _ in range(SUB)]
    move_leg_path(leg, swing_path)

    # 3. Drop down
    drop_path = [(0, -dt_swing) for _ in range(SUB)]
    move_leg_path(leg, drop_path)

# ------------------------------------------------------------
# DIAGONAL STEP
# ------------------------------------------------------------
def diagonal_step(pair_push, pair_lift):
    # Move lifted legs simultaneously
    for i in range(SUB):
        for leg in pair_lift:
            df = 0
            dt = (TIBIA_SIGN[leg] * LIFT_TIBIA) / SUB
            angles[leg]["T"] += dt
            kit.servo[legs[leg]["T"]].angle = angles[leg]["T"]

        # Push grounded legs back simultaneously
        for leg in pair_push:
            df = FEMUR_SIGN[leg] * FEMUR_PUSH / SUB
            dt = 0
            angles[leg]["F"] += df
            angles[leg]["T"] += dt
            kit.servo[legs[leg]["F"]].angle = angles[leg]["F"]
            kit.servo[legs[leg]["T"]].angle = angles[leg]["T"]
        time.sleep(DT)

    # Swing lifted legs forward
    for i in range(SUB):
        for leg in pair_lift:
            df = -FEMUR_SIGN[leg] * FEMUR_PUSH / SUB
            dt = -TIBIA_SIGN[leg] * LIFT_TIBIA / SUB
            angles[leg]["F"] += df
            angles[leg]["T"] += dt
            kit.servo[legs[leg]["F"]].angle = angles[leg]["F"]
            kit.servo[legs[leg]["T"]].angle = angles[leg]["T"]
        time.sleep(DT)

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
