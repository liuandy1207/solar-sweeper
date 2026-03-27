from pynput import keyboard
import serial

PORT = "/dev/tty.usbmodem2101"  # specific port on my computer to rpi pico
ser = serial.Serial(PORT, 115200)

def on_press(key):
    try:
        if key.char in ('w', 'a', 's', 'd'):
            ser.write(key.char.encode())
    except AttributeError:
        pass  # special key, ignore

with keyboard.Listener(on_press=on_press) as listener:
    print("WASD to move, Ctrl+C to quit")
    listener.join()