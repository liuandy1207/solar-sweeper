# =============================================================================
# code.py
# -----------------------------------------------------------------------------
# CircuitPython code for the Raspberry Pi Pico that sends movement signals to
# the TMC2209 motor driver from serial input sent by keyboard_controls.py
# =============================================================================

# imports
import board        # allows access to pins by name
import digitalio    # allows the setting of pin direction and value
import time         # allows delay between processes
import sys          # allows serial input to be read
import supervisor   # allows the checking of the serial port w/o blocking

# pin setup for the y-direction (along the rails, two motors)
dir_y = digitalio.DigitalInOut(board.GP2)
dir_y.direction = digitalio.Direction.OUTPUT
step_y = digitalio.DigitalInOut(board.GP3)
step_y.direction = digitalio.Direction.OUTPUT
en_y = digitalio.DigitalInOut(board.GP4)
en_y.direction = digitalio.Direction.OUTPUT

# pin setup for the x-direction (between the rails, one motor)
dir_x = digitalio.DigitalInOut(board.GP6)
dir_x.direction = digitalio.Direction.OUTPUT
step_x = digitalio.DigitalInOut(board.GP7)
step_x.direction = digitalio.Direction.OUTPUT
en_x = digitalio.DigitalInOut(board.GP8)
en_x.direction = digitalio.Direction.OUTPUT

# initial states
en_y.value = False  # active low enable
en_x.value = False
step_y.value = False
step_x.value = False
dir_y.value = True
dir_x.value = True

# constants
STEP_DELAY = 0.002
STEPS_PER_KEY = 200

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

def read_key():
    """"
    Reads a single keypress from serial input without blocking.

    Returns:
        str: The character read or None if no input is available.
    """
    if not supervisor.runtime.serial_bytes_available:
        return None
    return sys.stdin.read(1)

# main function loop
while True:
    key = read_key()        # read a key
    if key == 'd':          # check key for direction
        dir_y.value = True  # set relevant direction
        time.sleep(0.005)   # delay for safety
        do_steps(step_y, STEPS_PER_KEY) # step the motor
        # clear out the serial because keys stack up when held, resulting
        # in a build up in commands otherwise
        while supervisor.runtime.serial_bytes_available:
            sys.stdin.read(1)
        time.sleep(0.05)
    # other keys follow a similar arrangement, but with different direcitons and/or motors
    elif key == 'a':
        dir_y.value = False
        time.sleep(0.005)
        do_steps(step_y, STEPS_PER_KEY)
        while supervisor.runtime.serial_bytes_available:
            sys.stdin.read(1)
        time.sleep(0.05)  
    elif key == 'w':
        dir_x.value = True
        time.sleep(0.005)
        do_steps(step_x, STEPS_PER_KEY)
        while supervisor.runtime.serial_bytes_available:
            sys.stdin.read(1)
        time.sleep(0.05)
    elif key == 's':
        dir_x.value = False
        time.sleep(0.005)
        do_steps(step_x, STEPS_PER_KEY)
        while supervisor.runtime.serial_bytes_available:
            sys.stdin.read(1)
        time.sleep(0.05)
