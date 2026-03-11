# imports
import board		# for board control
import digitalio	# for io control
import time			# for delays

# pin setup
dir_x = digitalio.DigitalInOut(board.GP2)		# sets spin direction (cw, ccw)
dir_x.direction = digitalio.Direction.OUTPUT
step_x = digitalio.DigitalInOut(board.GP3)		# advances motor on rising edge
step_x.direction = digitalio.Direction.OUTPUT
en_x = digitalio.DigitalInOut(board.GP4)
en_x.direction = digitalio.Direction.OUTPUT		# active low enable

# initial states
en_x.value = False
step_x.value = False
dir_x.value = False

while True:
    for i in range(20000):
        step_x.value = True
        time.sleep(0.005)
        step_x.value = False
        time.sleep(0.005)
        
    time.sleep(1)


# use uart to go into spreadcycle which is faster



