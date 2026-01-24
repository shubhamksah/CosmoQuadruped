import time
from adafruit_servokit import ServoKit
import sys
import tty
import termios

# Initialize ServoKit for 16 channels
kit = ServoKit(channels=16)

# Map legs and joints
# H = Hip, F = Femur, T = Tibia
legs = {
    "FL": {"H": 2, "F": 1, "T": 0},
    "FR": {"H": 5, "F": 4, "T": 3},
    "BL": {"H": 8, "F": 7, "T": 6},
    "BR": {"H": 11, "F": 10, "T": 9}
}

# =========================
# Base angles (physically straight)
# These should match REAL straight joints
# =========================
base_angles = {
    "FL": {"H": 100, "F": (96 + 45), "T": 90},
    "FR": {"H": 88,  "F": (92 - 45), "T": 90},
    "BL": {"H": 96,  "F": (88 + 45), "T": 90},
    "BR": {"H": 94,  "F": (87 - 45), "T": 90}
}

# Initialize angles to base positions
angles = {
    leg: {joint: base_angles[leg][joint] for joint in joints}
    for leg, joints in legs.items()
}

# Apply base angles at startup
for leg_name, joints in legs.items():
    for joint_name, servo_index in joints.items():
        kit.servo[servo_index].angle = angles[leg_name][joint_name]

# Read single keypress (arrow keys)
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

# Tweak one joint with live feedback
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

# Main loop
def main():
    print("Quadruped Joint Tweaker (Anatomically Correct)")
    print("Legs: FL FR BL BR")
    print("Joints: H = Hip | F = Femur | T = Tibia")
    print("Type 'exit' to quit\n")

    try:
        while True:
            leg = input("Leg: ").upper()
            if leg == "EXIT":
                break
            if leg not in legs:
                print("Invalid leg")
                continue

            joint = input("Joint (H/F/T): ").upper()
            if joint == "EXIT":
                break
            if joint not in legs[leg]:
                print("Invalid joint")
                continue

            tweak_servo(leg, joint, legs[leg][joint])

    except KeyboardInterrupt:
        print("\nExiting...")

    # Print final calibration
    print("\nFinal calibrated base angles:")
    for leg in angles:
        for joint in angles[leg]:
            print(f"{leg} {joint}: {angles[leg][joint]}°")

if __name__ == "__main__":
    main()
