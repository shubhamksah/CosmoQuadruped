import time
import pygame
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

# Default positions mapped by servo index
default_positions = {
    0: 90,   # FLT
    1: 90,  # FLF
    2: 90,  # FLH
    3: 90,   # FRT
    4: 90,   # FRF
    5: 90,   # FRH
    6: 90,   # BLT
    7: 90,  # BLF
    8: 90,   # BLH
    9: 90,   # BRT
    10: 90,  # BRF
    11: 90   # BRH
}

try:
    for servo_index, angle in default_positions.items():
        kit.servo[servo_index].angle = angle

except KeyboardInterrupt:
    print("Exiting...")
    quit()
