import time
from adafruit_servokit import ServoKit
import sys
import tty
import termios

# ============================================================
# QUADRUPED SERVO TWEAKER + CALIBRATION TOOL
# ============================================================

kit = ServoKit(channels=16)

# ------------------------------------------------------------
# SERVO CHANNEL MAP
# ------------------------------------------------------------
legs = {
    "FL": {"H": 2,  "F": 1,  "T": 0},
    "FR": {"H": 5,  "F": 4,  "T": 3},
    "BL": {"H": 8,  "F": 7,  "T": 6},
    "BR": {"H": 11, "F": 10, "T": 9}
}

# ------------------------------------------------------------
# BASE ANGLES (CALIBRATED NEUTRAL)
# ------------------------------------------------------------
base_angles = {
    "FL": {"H": 100, "F": (96 + 45), "T": 90},
    "FR": {"H": 88,  "F": (92 - 45), "T": 82},
    "BL": {"H": 96,  "F": (88 + 45), "T": 85},
    "BR": {"H": 94,  "F": (87 - 45), "T": 91}
}

# ------------------------------------------------------------
# LIVE ANGLE STATE
# ------------------------------------------------------------
angles = {
    leg: {joint: base_angles[leg][joint] for joint in joints}
    for leg, joints in legs.items()
}

# ------------------------------------------------------------
# APPLY BASE ANGLES
# ------------------------------------------------------------
for leg_name, joints in legs.items():
    for joint_name, servo_index in joints.items():
        kit.servo[servo_index].angle = angles[leg_name][joint_name]
        time.sleep(0.05)

# ------------------------------------------------------------
# RAW KEY INPUT
# ------------------------------------------------------------
def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch1 = sys.stdin.read(1)
        if ch1 == "\x1b":
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            return ch1 + ch2 + ch3
        return ch1
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# ------------------------------------------------------------
# TWEAK SINGLE JOINT
# ------------------------------------------------------------
def tweak_single(leg, joint):
    servo_index = legs[leg][joint]
    print(f"\nTweaking {leg} {joint}")
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
        print(f"{leg} {joint}: {angles[leg][joint]}°   ", end="\r")

# ------------------------------------------------------------
# TWEAK ALL OF ONE JOINT TYPE (H / F / T)
# ------------------------------------------------------------
def tweak_group(joint):
    print(f"\nTweaking ALL {joint} joints together")
    print("↑ increase | ↓ decrease | q = done\n")

    while True:
        key = get_key()

        if key == "\x1b[A":
            for leg in legs:
                if angles[leg][joint] < 180:
                    angles[leg][joint] += 1
        elif key == "\x1b[B":
            for leg in legs:
                if angles[leg][joint] > 0:
                    angles[leg][joint] -= 1
        elif key.lower() == "q":
            print("\nFinal angles:")
            for leg in legs:
                print(f"{leg} {joint}: {angles[leg][joint]}°")
            print()
            break

        for leg in legs:
            kit.servo[legs[leg][joint]].angle = angles[leg][joint]

        status = " | ".join(
            f"{leg}:{angles[leg][joint]}°" for leg in legs
        )
        print(status + "   ", end="\r")

# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
def main():
    print("\nQuadruped Calibration Tool")
    print("Perspective: FROM BEHIND, looking forward\n")
    print("Individual: FL FR BL BR")
    print("Groups: ALL_H  ALL_F  ALL_T")
    print("Type 'exit' to quit\n")

    try:
        while True:
            cmd = input("Leg / Group: ").upper()
            if cmd == "EXIT":
                break

            if cmd in ["ALL_H", "ALL_F", "ALL_T"]:
                tweak_group(cmd[-1])
                continue

            if cmd not in legs:
                print("Invalid leg or group")
                continue

            joint = input("Joint (H/F/T): ").upper()
            if joint not in ["H", "F", "T"]:
                print("Invalid joint")
                continue

            tweak_single(cmd, joint)

    except KeyboardInterrupt:
        print("\nExiting...")

    print("\nFinal calibrated base angles:")
    for leg in angles:
        for joint in angles[leg]:
            print(f"{leg} {joint}: {angles[leg][joint]}°")

# ------------------------------------------------------------
if __name__ == "__main__":
    main()
