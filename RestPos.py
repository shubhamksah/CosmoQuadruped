import time
from adafruit_servokit import ServoKit
import sys
import tty
import termios

# Initialize ServoKit for 16 channels
kit = ServoKit(channels=16)

# Map legs and joints (H = hip, T = thigh, F = foot)
legs = {
    "FL": {"H": 2, "T": 0, "F": 1},
    "FR": {"H": 5, "T": 3, "F": 4},
    "BL": {"H": 8, "T": 6, "F": 7},
    "BR": {"H": 11, "T": 9, "F": 10}
}

# =========================
# Base angles (physically straight)
# Change these values after calibrating with tweaker
# =========================
base_angles = {
    "FL": {"H": 100, "T": 90, "F": 90},
    "FR": {"H": 88, "T": 90, "F": 90},
    "BL": {"H": 96, "T": 90, "F": 90},
    "BR": {"H": 94, "T": 90, "F": 90}
}

# Initialize angles to base positions
angles = {leg: {joint: base_angles[leg][joint] for joint in joints} for leg, joints in legs.items()}

# Apply base angles to servos at program start
for leg_name, joints in legs.items():
    for joint_name, servo_index in joints.items():
        kit.servo[servo_index].angle = angles[leg_name][joint_name]

# Function to read single keypress (arrow keys included)
def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch1 = sys.stdin.read(1)
        if ch1 == "\x1b":  # arrow keys start with escape
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            return ch1 + ch2 + ch3
        else:
            return ch1
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# Function to tweak a single servo with live feedback
def tweak_servo(leg, joint, servo_index):
    print(f"\nTweaking {leg} {joint} (servo {servo_index})")
    print("Use ↑ to increase, ↓ to decrease, q to finish this joint\n")
    
    while True:
        key = get_key()
        if key == "\x1b[A":  # Up arrow
            if angles[leg][joint] < 180:
                angles[leg][joint] += 1
                kit.servo[servo_index].angle = angles[leg][joint]
        elif key == "\x1b[B":  # Down arrow
            if angles[leg][joint] > 0:
                angles[leg][joint] -= 1
                kit.servo[servo_index].angle = angles[leg][joint]
        elif key.lower() == "q":
            print(f"\nFinished {leg} {joint} at {angles[leg][joint]}°\n")
            break
        
        # Live feedback
        print(f"{leg} {joint} angle: {angles[leg][joint]}°   ", end="\r")

# Main program
def main():
    print("Quadruped Joint Tweaker with Base Angles")
    print("Legs: FL, FR, BL, BR | Joints: H (hip), T (thigh), F (foot)")
    print("Type 'exit' at any prompt to quit.\n")
    
    try:
        while True:
            leg = input("Enter leg: ").upper()
            if leg == "EXIT":
                break
            if leg not in legs:
                print("Invalid leg. Try again.")
                continue

            joint = input("Enter joint (H/T/F): ").upper()
            if joint == "EXIT":
                break
            if joint not in ["H","T","F"]:
                print("Invalid joint. Try again.")
                continue

            servo_index = legs[leg][joint]
            tweak_servo(leg, joint, servo_index)
    
    except KeyboardInterrupt:
        print("\nExiting program.")

    # Print final angles
    print("\nFinal calibrated angles (degrees):")
    for leg_name, joints in angles.items():
        for joint_name, angle in joints.items():
            print(f"{leg_name} {joint_name}: {angle}°")

if __name__ == "__main__":
    main()
