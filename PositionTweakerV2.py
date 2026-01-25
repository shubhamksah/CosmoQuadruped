import time
from adafruit_servokit import ServoKit
import sys
import tty
import termios

# ============================================================
# QUADRUPED SERVO TWEAKER + CALIBRATION TOOL
#
# PURPOSE:
# - Manually tweak individual joints using keyboard arrows
# - Calibrate "base angles" (true straight / neutral positions)
# - Provide a canonical reference for joint directions and signs
#
# VIEWING REFERENCE FRAME (VERY IMPORTANT):
# - Imagine standing BEHIND the robot
# - You are looking FORWARD toward the head
# - Left/right are from THIS perspective
#
# THIS FILE IS THE SINGLE SOURCE OF TRUTH
# for servo orientation, joint direction, and sign conventions.
# ============================================================


# ------------------------------------------------------------
# Initialize ServoKit for PCA9685 (16 channels)
# ------------------------------------------------------------
kit = ServoKit(channels=16)


# ------------------------------------------------------------
# SERVO CHANNEL MAP
#
# Joint naming:
#   H = Hip   (rotates leg left/right relative to body)
#   F = Femur (upper leg segment)
#   T = Tibia (lower leg segment / knee extension)
#
# IMPORTANT MECHANICAL NOTES:
# - Femur servo is the LOWER servo in the vertical stack
# - Tibia servo is the UPPER servo in the vertical stack
# - Their shafts face OPPOSITE directions
#
# - Front hip servos face FORWARD (away from body center)
# - Back hip servos face BACKWARD (away from body center)
# - All hip servo shafts point UPWARD
#
# Channel numbers MUST match wiring on PCA9685
# ------------------------------------------------------------
legs = {
    "FL": {"H": 2,  "F": 1,  "T": 0},
    "FR": {"H": 5,  "F": 4,  "T": 3},
    "BL": {"H": 8,  "F": 7,  "T": 6},
    "BR": {"H": 11, "F": 10, "T": 9}
}


# ------------------------------------------------------------
# BASE ANGLES (PHYSICALLY STRAIGHT / NEUTRAL)
#
# These angles represent the REAL, PHYSICAL neutral pose:
# - Femur is ~45° back from the Y-axis
# - Tibia horn is ~180° from X-axis
# - Robot stands naturally upright
#
# THESE VALUES ARE *NOT* ASSUMED TO BE 90°
# THEY ARE EMPIRICALLY MEASURED AND CALIBRATED
#
# Changing wording (foot → femur, thigh → tibia)
# DOES NOT CHANGE THESE VALUES.
# ------------------------------------------------------------
base_angles = {
    "FL": {"H": 100, "F": (96 + 45), "T": 90},
    "FR": {"H": 88,  "F": (92 - 45), "T": 82},
    "BL": {"H": 96,  "F": (88 + 45), "T": 85},
    "BR": {"H": 94,  "F": (87 - 45), "T": 91}
}


# ------------------------------------------------------------
# ANGLE STATE STORAGE
#
# angles[leg][joint] ALWAYS stores:
# - The ACTUAL servo angle in degrees (0–180)
# - Not offsets, not deltas, not virtual values
#
# This dictionary is the live truth of the robot state
# ------------------------------------------------------------
angles = {
    leg: {joint: base_angles[leg][joint] for joint in joints}
    for leg, joints in legs.items()
}


# ------------------------------------------------------------
# APPLY BASE ANGLES AT STARTUP
#
# Robot immediately moves into calibrated neutral pose
# ------------------------------------------------------------
for leg_name, joints in legs.items():
    for joint_name, servo_index in joints.items():
        kit.servo[servo_index].angle = angles[leg_name][joint_name]


# ------------------------------------------------------------
# KEYBOARD INPUT (RAW MODE)
#
# Allows reading single key presses including arrow keys
# WITHOUT needing Enter
# ------------------------------------------------------------
def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch1 = sys.stdin.read(1)
        if ch1 == "\x1b":          # Escape sequence (arrow keys)
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            return ch1 + ch2 + ch3
        return ch1
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


# ------------------------------------------------------------
# JOINT DIRECTION REFERENCE (CRITICAL SECTION)
#
# POSITIVE ANGLE INCREASE EFFECTS
#
# NOTE ON TERMINOLOGY:
# - "Tibia moves DOWN" means:
#     → knee EXTENDS
#     → foot pushes toward ground
#     → BODY MOVES UP (robot stands taller)
#
# This avoids confusion between joint motion and body motion.
#
# FROM BEHIND, LOOKING FORWARD:
#
# FRONT LEFT (FL):
#   +Hip    → rotates CLOCKWISE
#   +Femur → leg swings BACK
#   +Tibia → leg EXTENDS (body UP, horn moves UP)
#
# BACK LEFT (BL):
#   +Hip    → rotates COUNTERCLOCKWISE
#   +Femur → leg swings BACK
#   +Tibia → leg EXTENDS (body UP, horn moves UP)
#
# FRONT RIGHT (FR):
#   +Hip    → rotates CLOCKWISE
#   +Femur → leg swings FORWARD
#   +Tibia → leg EXTENDS (body UP, horn moves DOWN)
#
# BACK RIGHT (BR):
#   +Hip    → rotates COUNTERCLOCKWISE
#   +Femur → leg swings FORWARD
#   +Tibia → leg EXTENDS (body UP, horn moves DOWN)
#
# DIFFERENCES LEFT vs RIGHT:
# - Caused by mirrored servo stacking
# - Shafts face opposite directions
# - Resulting horn motion is inverted
#
# IMPORTANT:
# - Despite horn differences, POSITIVE tibia always = BODY UP
# ------------------------------------------------------------

# ------------------------------------------------------------
# PHYSICAL → SERVO DIRECTION MULTIPLIERS
#
# These values convert a PHYSICAL joint intent into the
# correct servo angle delta for each leg.
#
# +1 means: servo angle increases
# -1 means: servo angle decreases
#
# This table is derived DIRECTLY from the joint direction
# reference above and MUST NOT BE MODIFIED casually.
# ------------------------------------------------------------
direction = {
    "H": {   # Hip
        "FL": +1,
        "FR": +1,
        "BL": -1,
        "BR": -1,
    },
    "F": {   # Femur
        "FL": +1,
        "BL": +1,
        "FR": -1,
        "BR": -1,
    },
    "T": {   # Tibia (EXTEND = BODY UP)
        "FL": +1,
        "BL": +1,
        "FR": -1,
        "BR": -1,
    }
}


# ------------------------------------------------------------
# TWEAK A SINGLE JOINT WITH LIVE FEEDBACK
# ------------------------------------------------------------
def tweak_servo(leg, joint, servo_index):
    print(f"\nTweaking {leg} {joint} (servo {servo_index})")
    print("↑ increase | ↓ decrease | q = done\n")

    while True:
        key = get_key()

        if key == "\x1b[A" and angles[leg][joint] < 180:
            angles[leg][joint] += 1
        elif key == "\x1b[B" and angles[leg][joint] > 0:
            angles[leg][joint] -= 1
        elif key.lower() == "q":
            print(f"\nFinal {leg} {joint}: {angles[leg][joint]}°\n")
            break

        kit.servo[servo_index].angle = angles[leg][joint]
        print(f"{leg} {joint} angle: {angles[leg][joint]}°   ", end="\r")

def tweak_group_physical(joint):
    print(f"\nTweaking ALL {joint} joints (PHYSICAL MOTION)")
    print("↑ = physical positive | ↓ = physical negative | q = done\n")

    while True:
        key = get_key()

        if key == "\x1b[A":
            physical_delta = +1
        elif key == "\x1b[B":
            physical_delta = -1
        elif key.lower() == "q":
            print("\nFinal angles:")
            for leg in legs:
                print(f"{leg} {joint}: {angles[leg][joint]}°")
            print()
            break
        else:
            continue

        for leg in legs:
            servo_delta = physical_delta * direction[joint][leg]
            new_angle = angles[leg][joint] + servo_delta

            if 0 <= new_angle <= 180:
                angles[leg][joint] = new_angle
                kit.servo[legs[leg][joint]].angle = new_angle

        status = " | ".join(
            f"{leg}:{angles[leg][joint]}°" for leg in legs
        )
        print(status + "   ", end="\r")

# ------------------------------------------------------------
# MAIN PROGRAM LOOP
# ------------------------------------------------------------
def main():
    print("Quadruped Joint Tweaker (Anatomically & Mechanically Correct)")
    print("Perspective: FROM BEHIND, looking toward head")
    print("Legs: FL FR BL BR")
    print("Joints: H = Hip | F = Femur | T = Tibia")
    print("Type 'exit' to quit\n")

    try:
        while True:
            cmd = input("Leg / Group: ").upper()
            if cmd == "EXIT":
                break

            if cmd in ["ALL_H", "ALL_F", "ALL_T"]:
                tweak_group_physical(cmd[-1])
                continue

            if cmd not in legs:
                print("Invalid leg or group")
                continue

            joint = input("Joint (H/F/T): ").upper()
            if joint not in legs[cmd]:
                print("Invalid joint")
                continue

            tweak_servo(cmd, joint, legs[cmd][joint])


    except KeyboardInterrupt:
        print("\nExiting...")


    # --------------------------------------------------------
    # FINAL CALIBRATION OUTPUT
    #
    # These values should be copied directly into base_angles
    # after physical alignment is confirmed.
    # --------------------------------------------------------
    print("\nFinal calibrated base angles:")
    for leg in angles:
        for joint in angles[leg]:
            print(f"{leg} {joint}: {angles[leg][joint]}°")


# ------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------
if __name__ == "__main__":
    main()
