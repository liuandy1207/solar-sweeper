# =============================================================================
# pico_controller.py
# -----------------------------------------------------------------------------
# CircuitPython code for the Raspberry Pi Pico that sends movement signals to
# the TMC2209 motor driver from input sent by simulation_controller.py
# =============================================================================

# imports
import math
import board        # allows access to pins by name
import digitalio    # allows the setting of pin direction and value
import time         # allows delay between processes
import usb_cdc      # for usb serial communication in CircuitPython

# pin setup for the x-direction (along the rails, two motors)
# note: this is inverted from other documentation
dir_x = digitalio.DigitalInOut(board.GP2)
dir_x.direction = digitalio.Direction.OUTPUT
step_x = digitalio.DigitalInOut(board.GP3)
step_x.direction = digitalio.Direction.OUTPUT
en_x = digitalio.DigitalInOut(board.GP4)
en_x.direction = digitalio.Direction.OUTPUT

# pin setup for the y-direction (between the rails, one motor)
# note: this is inverted from other documentation
dir_y = digitalio.DigitalInOut(board.GP6)
dir_y.direction = digitalio.Direction.OUTPUT
step_y = digitalio.DigitalInOut(board.GP7)
step_y.direction = digitalio.Direction.OUTPUT
en_y = digitalio.DigitalInOut(board.GP8)
en_y.direction = digitalio.Direction.OUTPUT

# initial states
en_y.value = False  # active low enable
en_x.value = False
step_y.value = False
step_x.value = False
dir_y.value = True
dir_x.value = True

def max_distance(total_axis_dist: float, r: float, N: int = 200) -> int:
    """
    Converts a physical axis length into a maximum step count.

    Args:
        total_axis_dist (float): Total travel distance in mm.
        r (float): Pulley radius in mm.
        N (int): Steps per revolution.

    Returns:
        int: Maximum number of steps across the axis.
    """
    mm_per_step = (2 * math.pi * r) / N
    return int(total_axis_dist / mm_per_step)

# tuning, proof of concept, values not exactly to scale
STEP_DELAY = 0.001
X_MIN = 0
Y_MIN = 0

X_MAX = max_distance(total_axis_dist=500.0, r=2.0, N=200)
Y_MAX = max_distance(total_axis_dist=750.0, r=2.0, N=200)

INVERT_X_DIR = True
INVERT_Y_DIR = False

current_x = 0
current_y = 0

# trivial
def clamp(val: int, low: int, high: int) -> int:
    '''
    Function to clamp val to be within low and high (inclusive)

    Args:
        val (int): value to clamp
        low (int): minimum allowed value
        high (int): maximum allowed value
    Returns:
        clamped value (int)
    '''
    return max(low, min(val, high))

def do_steps(step_pin, n):
    """
    Moves the brush in a specified direction for a certain number of steps.

    Args:
        step_pin (digitalio.DigitalInOut): the step pin of the relevant motor 
        n (int): the number of steps to move
    Returns:
        None
    """
    for _ in range(n):
        step_pin.value = True
        time.sleep(STEP_DELAY)
        step_pin.value = False
        time.sleep(STEP_DELAY)

def move_to(new_x: int, new_y: int):
    """
    Moves the brush carriage to an absolute (x, y) step position.

    Args:
        new_x (int): Target X position in steps.
        new_y (int): Target Y position in steps.
    """
    global current_x, current_y

    new_x = clamp(new_x, X_MIN, X_MAX)
    new_y = clamp(new_y, Y_MIN, Y_MAX)

    dx = new_x - current_x
    dy = new_y - current_y

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


serial = usb_cdc.data       # open serial channel for inputs
buffer = ""                 # allows incoming character to accumulate

print("pico motor init")

# main code loop
while True:
    if serial.in_waiting > 0:
        data = serial.read(serial.in_waiting)      # read all incoming bytes
        if data:
            try:
                buffer += data.decode("utf-8")     # decode and save keys
            except UnicodeError:
                pass

            # process complete lines in buffer
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip().upper()

                if not line:
                    continue

                if line == "STOP":
                    # disable both motors
                    en_x.value = True
                    en_y.value = True
                    continue

                if line == "PARK":
                    # return the brush to the origin
                    move_to(0, 0)
                    continue
                
                parts = line.split()    # split command and coordinates
                # expected: "MOVE 123 456"
                if len(parts) == 3 and parts[0] == "MOVE":
                    try:
                        x = int(parts[1])
                        y = int(parts[2])
                        move_to(x, y)
                    except ValueError:
                        pass