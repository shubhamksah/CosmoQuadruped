import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

legs = {
    "FL": {"H": 2, "F": 1, "T": 0},
    "FR": {"H": 5, "F": 4, "T": 3},
    "BL": {"H": 8, "F": 7, "T": 6},
    "BR": {"H": 11, "F": 10, "T": 9}
}

# BASE (YOUR CALIBRATED STRAIGHT STANCE)
base = {
    "FL": {"H": 100, "F": 141, "T": 90},
    "FR": {"H": 88,  "F": 47,  "T": 82},
    "BL": {"H": 96,  "F": 133, "T": 85},
    "BR": {"H": 94,  "F": 42,  "T": 91}
}

LIMITS = {
    "FL": {"H": (80, 120), "F": (110, 160), "T": (70, 110)},
    "FR": {"H": (70, 110), "F": (30, 80),   "T": (65, 100)},
    "BL": {"H": (80, 120), "F": (110, 160), "T": (70, 110)},
    "BR": {"H": (80, 120), "F": (30, 80),   "T": (70, 110)},
}

angles = {l: dict(base[l]) for l in base}

def clamp(leg, joint, val):
    lo, hi = LIMITS[leg][joint]
    return max(lo, min(hi, val))

def set_joint(leg, joint, val):
    val = clamp(leg, joint, val)
    angles[leg][joint] = val
    kit.servo[legs[leg][joint]].angle = val

def stand_all():
    for leg in legs:
        for j in legs[leg]:
            set_joint(leg, j, base[leg][j])
    time.sleep(1)

def lift_body(except_leg):
    for leg in legs:
        if leg != except_leg:
            set_joint(leg, "T", angles[leg]["T"] + 8)
    time.sleep(0.4)

def relax_body():
    for leg in legs:
        set_joint(leg, "T", base[leg]["T"])
    time.sleep(0.4)

def step_leg(leg, direction):
    # unload
    set_joint(leg, "T", angles[leg]["T"] - 12)
    time.sleep(0.3)

    # swing
    set_joint(leg, "F", angles[leg]["F"] + direction)
    time.sleep(0.4)

    # plant
    set_joint(leg, "T", base[leg]["T"] + 6)
    time.sleep(0.4)

def creep_step():
    sequence = [
        ("FL", +12),
        ("BR", -12),
        ("FR", -12),
        ("BL", +12),
    ]

    for leg, femur_delta in sequence:
        lift_body(leg)
        step_leg(leg, femur_delta)
        relax_body()

# ---- RUN ----
stand_all()
time.sleep(1)

while True:
    creep_step()
