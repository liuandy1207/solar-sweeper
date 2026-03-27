'''
(this is code.py on the CircuitPython side)
'''

from __future__ import annotations

import math
import board
import digitalio
import time
import usb_cdc

def max_distance(total_axis_dist: float, r: float, N: int = 200) -> float:
    perstep = (2 * math.pi * r) / N
    return total_axis_dist / perstep

'''
Pin setup and initialize initial states
'''
# axes (two stepper drivers)
dir_x1 = digitalio.DigitalInOut(board.GP2)
dir_x1.direction = digitalio.Direction.OUTPUT

step_x1 = digitalio.DigitalInOut(board.GP3)
step_x1.direction = digitalio.Direction.OUTPUT

en_x1 = digitalio.DigitalInOut(board.GP4)
en_x1.direction = digitalio.Direction.OUTPUT

dir_x2 = digitalio.DigitalInOut(board.GP10)
dir_x2.direction = digitalio.Direction.OUTPUT

step_x2 = digitalio.DigitalInOut(board.GP11)
step_x2.direction = digitalio.Direction.OUTPUT

en_x2 = digitalio.DigitalInOut(board.GP12)
en_x2.direction = digitalio.Direction.OUTPUT

# Y axis
dir_y = digitalio.DigitalInOut(board.GP6)
dir_y.direction = digitalio.Direction.OUTPUT

step_y = digitalio.DigitalInOut(board.GP7)
step_y.direction = digitalio.Direction.OUTPUT

en_y = digitalio.DigitalInOut(board.GP8)
en_y.direction = digitalio.Direction.OUTPUT

# Active low:
en_x1.value = False
en_x2.value = False
en_y.value = False

step_x1.value = False
step_x2.value = False
step_y.value = False

dir_x1.value = False
dir_x2.value = False
dir_y.value = False

'''
Motion tuning
'''
STEP_DELAY = 0.001
IDLE_DELAY = 0.002

# NOTE: set these after calibration
X_MIN = 0
X_MAX = max_distance(r=2, N=200, total_axis_dist=None)
Y_MIN = 0
Y_MAX = max_distance(r=2, N=200, total_axis_dist=None)

# Current and target position in step pulses
# X1 and X2 are treated as one logical X axis
current_x = 0
current_y = 0
target_x = 0
target_y = 0

# Direction inversion flags
# Often one X motor must be inverted if mounted mirrored
INVERT_X1_DIR = False
INVERT_X2_DIR = True
INVERT_Y_DIR = False

'''
Motor control (helper) functions
'''
def clamp(val: int, low: int, high: int) -> int:
    '''
    Clamp val to the range [low, high]

    :param val: The value to clamp
    :param low: The minimum allowed value
    :param high: The maximum allowed value

    :return: The clamped value
    '''
    return max(low, min(val, high))

def enable_motors():
    '''
    Enable all motors (active low)
    '''
    en_x1.value = False
    en_x2.value = False
    en_y.value = False

def disable_motors():
    '''
    Disable all motors (active low)
    '''
    en_x1.value = True
    en_x2.value = True
    en_y.value = True

def set_dir_x(forward: bool):
    '''
    Set both X motor directions for synchronized X movement.
    Each motor may have its own inversion flag.

    :param forward: True for positive direction, False for negative direction
    '''
    val_x1 = forward
    if INVERT_X1_DIR:
        val_x1 = not val_x1
    dir_x1.value = val_x1

    val_x2 = forward
    if INVERT_X2_DIR:
        val_x2 = not val_x2
    dir_x2.value = val_x2


def set_dir_y(forward: bool):
    '''
    Set Y direction pin based on desired direction and inversion setting

    :param forward: True for positive direction, False for negative direction
    '''
    val = forward
    if INVERT_Y_DIR:
        val = not val
    dir_y.value = val


def pulse_step(step_pin: digitalio.DigitalInOut):
    '''
    Pulse one step pin once (HIGH -> LOW) with appropriate delay

    :param step_pin: The step pin to pulse
    '''
    step_pin.value = True
    time.sleep(STEP_DELAY)
    step_pin.value = False
    time.sleep(STEP_DELAY)


def pulse_step_pair(
    step_pin_a: digitalio.DigitalInOut,
    step_pin_b: digitalio.DigitalInOut
):
    '''
    Pulse two step pins together for synchronized motion

    :param step_pin_a: The first step pin to pulse
    :param step_pin_b: The second step pin to pulse
    '''
    step_pin_a.value = True
    step_pin_b.value = True
    time.sleep(STEP_DELAY)
    step_pin_a.value = False
    step_pin_b.value = False
    time.sleep(STEP_DELAY)


def move_x_steps(num_steps: int, forward: bool) -> None:
    '''
    Move the X axis a specific number of steps in a given direction.
    X1 and X2 move together.
    '''
    if num_steps <= 0:
        return

    enable_motors()
    set_dir_x(forward)

    for _ in range(num_steps):
        pulse_step_pair(step_x1, step_x2)


def move_y_steps(num_steps: int, forward: bool) -> None:
    '''
    Move the Y axis a specific number of steps in a given direction
    '''
    if num_steps <= 0:
        return

    enable_motors()
    set_dir_y(forward)

    for _ in range(num_steps):
        pulse_step(step_y)


def move_x(new_target_x: int) -> None:
    '''
    Move X axis to a specific target position (in steps),
    updating current_x accordingly
    '''
    global current_x

    new_target_x = clamp(new_target_x, X_MIN, X_MAX)

    if new_target_x > current_x:
        move_x_steps(new_target_x - current_x, True)
    elif new_target_x < current_x:
        move_x_steps(current_x - new_target_x, False)

    current_x = new_target_x


def move_y(new_target_y: int) -> None:
    '''
    Move Y axis to a specific target position (in steps),
    updating current_y accordingly
    '''
    global current_y

    new_target_y = clamp(new_target_y, Y_MIN, Y_MAX)

    if new_target_y > current_y:
        move_y_steps(new_target_y - current_y, True)
    elif new_target_y < current_y:
        move_y_steps(current_y - new_target_y, False)

    current_y = new_target_y


def step_toward_target() -> bool:
    '''
    Take a single logical step toward the current target position,
    updating current_x and current_y accordingly.
    Returns True if any motion occurred.
    '''
    global current_x, current_y

    moved = False

    if current_x < target_x:
        set_dir_x(True)
        pulse_step_pair(step_x1, step_x2)
        current_x += 1
        moved = True
    elif current_x > target_x:
        set_dir_x(False)
        pulse_step_pair(step_x1, step_x2)
        current_x -= 1
        moved = True

    if current_y < target_y:
        set_dir_y(True)
        pulse_step(step_y)
        current_y += 1
        moved = True
    elif current_y > target_y:
        set_dir_y(False)
        pulse_step(step_y)
        current_y -= 1
        moved = True

    return moved


def handle_command(line: str) -> None:
    '''
    Receive command line from host to perform action

    Example:
    MOVE 800 300
    STOP
    PARK
    '''
    global target_x, target_y, current_x, current_y

    line = line.strip()

    if not line:
        return

    if line == "STOP":
        target_x = current_x
        target_y = current_y
        return

    if line == "PARK":
        #NOTE: Temporary placeholder: defining a parking position as home (at end of panel)
        current_x = 0
        current_y = 0
        target_x = 0
        target_y = 0
        return

    parts = line.split()

    if len(parts) == 3 and parts[0] == "MOVE":
        try:
            x = int(parts[1])
            y = int(parts[2])
            target_x = clamp(x, X_MIN, X_MAX)
            target_y = clamp(y, Y_MIN, Y_MAX)
        except ValueError:
            pass

'''
Serial setup from Pico side
'''
serial = usb_cdc.data
# or if usb_cdc is disabled on board setup:
# serial = usb_cdc.console
buffer = ""

print("pico motor init")

'''
Main loop
'''
while True:
    # Read serial input
    if serial.in_waiting > 0:
        data = serial.read(serial.in_waiting)
        if data:
            try:
                buffer += data.decode("utf-8")
            except UnicodeError:
                pass

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                handle_command(line)

    # Move one logical step at a time toward target
    enable_motors()
    moved = step_toward_target()

    if not moved:
        disable_motors()
        time.sleep(IDLE_DELAY)