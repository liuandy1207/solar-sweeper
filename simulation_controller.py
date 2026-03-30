# =============================================================================
# simulation_controller.py
# -----------------------------------------------------------------------------
# The Pygame controller code for sending movement commands to the microcontroller.
# This is done via touch-to-move on the Pygame UI simulation, which then translates 
# into hardware coordinates and sends the command over serial.
# =============================================================================

import pygame
import sys
import math
import serial
import time
from typing import Tuple

'''
Serial Settings
- For connecting to the PORT of the microcontroller to allow control via the pygame simulation on a separate device.
- `send_line` sends the control text to the microcontroller
'''
USE_SERIAL = True
PORT = "/dev/tty.usbmodem2101"
BAUD = 115200

ser = None
if USE_SERIAL:
    try:
        ser = serial.Serial(PORT, BAUD, timeout=0.05)
        time.sleep(2)
        print(f"Connected to {PORT}")
    except Exception as e:
        print(f"Could not open serial port: {e}")
        ser = None

def send_line(text: str):
    '''
    Void function for sending control text to microcontroller via serial connection
    
    Args:
        text (string): The control command to send
    '''
    global ser
    if ser:
        ser.write((text + "\n").encode("utf-8"))
    print(">", text)

'''
Pygame Simulation Setup
- Allow for simulated + visual environment on the laptop screen for control
- Hardware mapping through pygame
'''
pygame.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulation + Hardware Mapping")

clock = pygame.time.Clock()

# Panel / rail area
panel_x = 150
panel_y = 120
panel_w = 500
panel_h = 320

# Carriage representation
car_w = 90
car_h = 60
car_x = panel_x + panel_w // 2 - car_w // 2
car_y = panel_y + panel_h // 2 - car_h // 2

move_speed = 4.0

# Target = center position of carriage
target_x = car_x + car_w / 2
target_y = car_y + car_h / 2

'''
HARDWARE MAPPING
'''
def max_distance(total_axis_dist: float, r: float, N: int = 200) -> float:
    '''
    Calculate theoretical linear distance for motor movement based on spool radius and steps per revolution
    d = (2 * pi * r) / N

    Args:
        total_axis_dist (float): Total linear distance of the (x or y) axis in mm
        r (int): Spool radius in mm
        N (int): Steps per revolution of the motor (200 steps/rev for Mini Nema)
    Returns:
        Linear distance in mm per step (float)
    '''
    if total_axis_dist is None:
        raise ValueError("total_axis_dist must be provided to calculate max distance")

    perstep = (2 * math.pi * r) / N
    max = total_axis_dist / perstep
    return max

#NOTE: Assuming the 200 steps/rev for the Mini Nema stepper, need to fix total_axis_dist by measurement later
hardware_X_max, hardware_Y_max = max_distance(r=2, N=200, total_axis_dist=500.0), max_distance(r=2, N=200, total_axis_dist=750.0)

def clamp(val: float, low: float, high: float) -> float:
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


def panel_to_hw(px: float, py: float) -> Tuple[int, int]:
    """
    Function to convert carriage center pixel position into hardware coordinates (steps)

    Args:
        px (float): Pixel x position of carriage center
        py (float): Pixel y position of carriage center
    Returns:
        Tuple of (hardware_x, hardware_y) in steps (Tuple of ints)
    """
    x_min = panel_x + car_w / 2
    x_max = panel_x + panel_w - car_w / 2
    y_min = panel_y + car_h / 2
    y_max = panel_y + panel_h - car_h / 2

    x_norm = (px - x_min) / (x_max - x_min)
    y_norm = (py - y_min) / (y_max - y_min)

    x_norm = clamp(x_norm, 0.0, 1.0)
    y_norm = clamp(y_norm, 0.0, 1.0)

    hw_x = int(round(x_norm * hardware_X_max))
    hw_y = int(round(y_norm * hardware_Y_max))
    return hw_x, hw_y


def hw_to_panel(hw_x: float, hw_y: float) -> Tuple[float, float]:
    '''
    Function to reverse map hardware coordinates (steps) to panel center position
    - Useful for visualization

    Args:
        hw_x (float): Hardware x position in steps
        hw_y (float): Hardware y position in steps
    Returns:
        Tuple of (pixel_x, pixel_y) for carriage center (Tuple of floats)
    '''
    x_min = panel_x + car_w / 2
    x_max = panel_x + panel_w - car_w / 2
    y_min = panel_y + car_h / 2
    y_max = panel_y + panel_h - car_h / 2

    x_norm = (hw_x / hardware_X_max) if hardware_X_max > 0 else 0.0
    y_norm = (hw_y / hardware_Y_max) if hardware_Y_max > 0 else 0.0

    x_norm = clamp(x_norm, 0.0, 1.0)
    y_norm = clamp(y_norm, 0.0, 1.0)

    px = x_min + x_norm * (x_max - x_min)
    py = y_min + y_norm * (y_max - y_min)
    return px, py

'''
Simulation Loop (for pygame)
- This provides the UI screen for clicking-to-moving from simulation to the physical hardware
'''
last_target = None

running = True
while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            send_line("STOP")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Accepting only clicks inside the panel and then clamping it
            if panel_x <= mx <= panel_x + panel_w and panel_y <= my <= panel_y + panel_h:
                target_x = max(panel_x + car_w / 2, min(mx, panel_x + panel_w - car_w / 2))
                target_y = max(panel_y + car_h / 2, min(my, panel_y + panel_h - car_h / 2))

                # translating to hardware coordinates and sending to microcontroller
                hw_x, hw_y = panel_to_hw(target_x, target_y)

                target_tuple = (hw_x, hw_y)
                if target_tuple != last_target:
                    send_line(f"MOVE {hw_x} {hw_y}")
                    last_target = target_tuple
                    print(f"Sent MOVE command: ({hw_x}, {hw_y})")

    # Current carriage center
    car_center_x = car_x + car_w / 2
    car_center_y = car_y + car_h / 2

    # Move toward target
    dx = target_x - car_center_x
    dy = target_y - car_center_y
    dist = math.hypot(dx, dy)

    if dist > move_speed:
        car_center_x += move_speed * dx / dist
        car_center_y += move_speed * dy / dist
    else:
        car_center_x = target_x
        car_center_y = target_y

    car_x = car_center_x - car_w / 2
    car_y = car_center_y - car_h / 2

    # draw
    screen.fill((240, 240, 240))

    pygame.draw.line(screen, (255, 100, 180), (50, HEIGHT - 50), (200, HEIGHT - 50), 3)
    pygame.draw.line(screen, (255, 100, 180), (50, HEIGHT - 50), (50, HEIGHT - 200), 3)

    pygame.draw.rect(screen, (80, 110, 150), (panel_x, panel_y, panel_w, panel_h), border_radius=4)
    pygame.draw.rect(screen, (40, 40, 40), (panel_x, panel_y, panel_w, panel_h), 3)

    pygame.draw.line(screen, (120, 120, 120), (panel_x, panel_y), (panel_x + panel_w, panel_y), 8)
    pygame.draw.line(screen, (120, 120, 120), (panel_x, panel_y + panel_h), (panel_x + panel_w, panel_y + panel_h), 8)

    car_center_x_int = int(car_x + car_w // 2)
    pygame.draw.line(screen, (230, 230, 230), (car_center_x_int, panel_y), (car_center_x_int, int(car_y)), 2)
    pygame.draw.line(screen, (230, 230, 230), (car_center_x_int, int(car_y + car_h)), (car_center_x_int, panel_y + panel_h), 2)

    pygame.draw.rect(screen, (180, 220, 255), (int(car_x), int(car_y), car_w, car_h))
    pygame.draw.rect(screen, (60, 90, 120), (int(car_x), int(car_y), car_w, car_h), 2)

    pygame.draw.circle(screen, (255, 80, 80), (int(target_x), int(target_y)), 5)

    sim_hw_x, sim_hw_y = panel_to_hw(car_x + car_w / 2, car_y + car_h / 2)
    tgt_hw_x, tgt_hw_y = panel_to_hw(target_x, target_y)

    info = [
        f"Simulation Pos: x={int(car_x - panel_x)}, y={int(car_y - panel_y)}",
        f"Simulation Hardware: x={sim_hw_x}, y={sim_hw_y}",
        f"Target HW: x={tgt_hw_x}, y={tgt_hw_y}",
    ]

    y_text = 20
    for line in info:
        # surf = font.render(line, True, (20, 20, 20))
        # screen.blit(surf, (20, y_text))
        y_text += 30

    pygame.display.flip()

pygame.quit()

if ser:
    ser.close()

sys.exit()