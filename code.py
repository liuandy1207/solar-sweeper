import board
import digitalio
import time
import sys
import supervisor

# pin setup
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

en_x.value = False
en_y.value = False
step_x.value = False
step_y.value = False
dir_x.value = True
dir_y.value = True

STEP_DELAY = 0.001
STEPS_PER_KEY = 200

def do_steps(step_pin, n):
    for _ in range(n):
        step_pin.value = True
        time.sleep(STEP_DELAY)
        step_pin.value = False
        time.sleep(STEP_DELAY)

def read_key():
    if not supervisor.runtime.serial_bytes_available:
        return None
    return sys.stdin.read(1)

while True:
    key = read_key()
    if key == 'd':
        dir_x.value = True
        do_steps(step_x, STEPS_PER_KEY)
    elif key == 'a':
        dir_x.value = False
        do_steps(step_x, STEPS_PER_KEY)
    elif key == 'w':
        dir_y.value = True
        do_steps(step_y, STEPS_PER_KEY)
    elif key == 's':
        dir_y.value = False
        do_steps(step_y, STEPS_PER_KEY)