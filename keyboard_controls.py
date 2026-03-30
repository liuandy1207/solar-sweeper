# =============================================================================
# keyboard_controls.py
# -----------------------------------------------------------------------------
# Sends characters to the serial. Must run with Thonny closed, or else 
# the port is occupied.
# =============================================================================

# imports
from pynput import keyboard     # allows listening for key presses
import serial                   # allows communication over serial

# CHANGE THIS IF YOUR COMPUTER HAS A DIFFERENT PORT FOR THE PICO
PORT = "/dev/tty.usbmodem2101"
ser = serial.Serial(PORT, 115200)   # open serial communication at 115200 baud rate

def on_press(key):
    """
    Sends WASD characters over serial; ignores all other keys.
    """
    try:
        if key.char in ('w', 'a', 's', 'd'):
            ser.write(key.char.encode())    # send as bytes
    except AttributeError:
        pass    # ignore when its a special key

# start the keyboard listener
with keyboard.Listener(on_press=on_press) as listener:
    print("WASD to move, Ctrl+C to quit")
    listener.join()