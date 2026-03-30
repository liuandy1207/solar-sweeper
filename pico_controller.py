from __future__ import annotations

import math
import board
import digitalio
import time
import usb_cdc

# max_distance function from simulation_controller.py. imports from other files doesn't work in CircuitPython
def max_distance(total_axis_dist: float, r: float, N: int = 200) -> int:
    per_step = (2 * math.pi * r) / N
    return int(total_axis_dist / per_step)

# Pins
dir_x = digitalio.DigitalInOut(board.GP2)
dir_x.direction = digitalio.Direction.OUTPUT

step_x = digitalio.DigitalInOut(board.GP3)
step_x.direction = digitalio.Direction.OUTPUT

en_x = digitalio.DigitalInOut(board.GP4)
en_x.direction = digitalio.Direction.OUTPUT

dir_y = digitalio.DigitalInOut(board.GP6)
dir_y.direction = digitalio.Direction.OUTPUT

step_y = digitalio.DigitalInOut(board.GP7)
step_y.direction = digitalio.Direction.OUTPUT

en_y = digitalio.DigitalInOut(board.GP8)
en_y.direction = digitalio.Direction.OUTPUT

# active-low enable
en_x.value = True
en_y.value = True

step_x.value = False
step_y.value = False

dir_x.value = False
dir_y.value = False

# Tuning
STEP_DELAY = 0.001
X_MIN = 0
Y_MIN = 0

X_MAX = max_distance(total_axis_dist=500.0, r=2.0, N=200)
Y_MAX = max_distance(total_axis_dist=750.0, r=2.0, N=200)

INVERT_X_DIR = True
INVERT_Y_DIR = False

current_x = 0
current_y = 0

def clamp(val: int, low: int, high: int) -> int:
    '''
    Function to clamp val to be within low and high (inclusive)

    :param val: value to clamp
    :param low: minimum allowed value
    :param high: maximum allowed value
    :return: clamped value
    '''
    return max(low, min(val, high))

def do_steps(step_pin, n: int) -> None:
    '''
    Function to pulse the given step pin n times with delay between changes

    :param step_pin: the digitalio pin connected to the step input of the driver
    :param n: number of steps to pulse
    '''
    for _ in range(n):
        step_pin.value = True
        time.sleep(STEP_DELAY)
        step_pin.value = False
        time.sleep(STEP_DELAY)

def move_to(new_x: int, new_y: int) -> None:
    '''
    Function to move the carriage to the specified (new_x, new_y) position in hardware coordinates

    :param new_x: target x position in steps
    :param new_y: target y position in steps
    '''
    global current_x, current_y

    new_x = clamp(new_x, X_MIN, X_MAX)
    new_y = clamp(new_y, Y_MIN, Y_MAX)

    dx = new_x - current_x
    dy = new_y - current_y

    # enable motors
    en_x.value = False
    en_y.value = False

    # move X
    if dx != 0:
        forward_x = dx > 0
        dir_x.value = (not forward_x) if INVERT_X_DIR else forward_x
        do_steps(step_x, abs(dx))
        current_x = new_x

    # move Y
    if dy != 0:
        forward_y = dy > 0
        dir_y.value = (not forward_y) if INVERT_Y_DIR else forward_y
        do_steps(step_y, abs(dy))
        current_y = new_y

    # disable motors after move
    en_x.value = True
    en_y.value = True

# serial
serial = usb_cdc.console
buffer = ""

print("pico motor init")

while True:
    if serial.in_waiting > 0:
        data = serial.read(serial.in_waiting)
        if data:
            try:
                buffer += data.decode("utf-8")
            except UnicodeError:
                pass

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip().upper()

                if not line:
                    continue

                if line == "STOP":
                    en_x.value = True
                    en_y.value = True
                    continue

                if line == "PARK":
                    move_to(0, 0)
                    continue

                parts = line.split()
                if len(parts) == 3 and parts[0] == "MOVE":
                    try:
                        x = int(parts[1])
                        y = int(parts[2])
                        move_to(x, y)
                    except ValueError:
                        pass