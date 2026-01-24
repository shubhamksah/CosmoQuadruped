import time
from adafruit_servokit import ServoKit
import sys
import tty
import termios

# Initialize ServoKit for 16 channels
kit = ServoKit(channels=16)

# Map legs and joints
legs = {
    "FL": {"H": 2, "T": 0, "F": 1},
    "FR": {"H": 5, "T": 3, "F": 4},
    "BL": {"H": 8, "T": 6, "F": 7},
    "BR": {"H": 11, "T": 9, "F": 10}
}

# Store current angles for each servo
angles = {servo: 90 for leg in legs.values() for servo in leg.values()}

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

# Function to tweak a single servo
def tweak_servo(servo_index):
    print(f"Adjusting servo {servo_index}. Use ↑/↓ to move, q to quit this servo.")
    while True:
        key = get_key()
        if key == "\x1b[A":  # Up arrow
            if angles[servo_index] < 180:
                angles[servo_index] += 1
                kit.servo[servo_index].angle = angles[servo_index]
        elif key == "\x1b[B":  # Down arrow
            if angles[servo_index] > 0:
                angles[servo_index] -= 1
                kit.servo[servo_index].angle = angles[servo_index]
        elif key.lower() == "q":
            print(f"Done tweaking servo {servo_index}.")
            break
        print(f"Servo {servo_index} angle: {angles[servo_index]}", end="\r")

# Main program
def main():
    print("Quadruped Joint Tweaker")
    print("Available legs: FL, FR, BL, BR")
    print("Available joints: H (hip), T (thigh), F (foot)")
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
            if joint not in ["H", "T", "F"]:
                print("Invalid joint. Try again.")
                continue

            servo_index = legs[leg][joint]
            tweak_servo(servo_index)

    except KeyboardInterrupt:
        print("\nExiting program.")

if __name__ == "__main__":
    main()

