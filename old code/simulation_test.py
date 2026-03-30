import pygame
import sys
import math

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulation")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

# Panel / rail area
panel_x = 150
panel_y = 120
panel_w = 500
panel_h = 320

# Carriage
car_w = 90
car_h = 60
car_x = panel_x + panel_w // 2 - car_w // 2
car_y = panel_y + panel_h // 2 - car_h // 2

move_speed = 4.0

# Target = carriage center position
target_x = car_x + car_w / 2
target_y = car_y + car_h / 2

running = True
while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Only accept clicks inside the panel
            if panel_x <= mx <= panel_x + panel_w and panel_y <= my <= panel_y + panel_h:
                # Clamp target so whole carriage stays inside panel
                target_x = max(panel_x + car_w / 2, min(mx, panel_x + panel_w - car_w / 2))
                target_y = max(panel_y + car_h / 2, min(my, panel_y + panel_h - car_h / 2))

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

    # Convert center back to top-left
    car_x = car_center_x - car_w / 2
    car_y = car_center_y - car_h / 2

    # Final clamp
    car_x = max(panel_x, min(car_x, panel_x + panel_w - car_w))
    car_y = max(panel_y, min(car_y, panel_y + panel_h - car_h))

    # Draw
    screen.fill((240, 240, 240))

    # Axes hint
    pygame.draw.line(screen, (255, 100, 180), (50, HEIGHT - 50), (200, HEIGHT - 50), 3)
    pygame.draw.line(screen, (255, 100, 180), (50, HEIGHT - 50), (50, HEIGHT - 200), 3)

    # Panel
    pygame.draw.rect(screen, (80, 110, 150), (panel_x, panel_y, panel_w, panel_h), border_radius=4)
    pygame.draw.rect(screen, (40, 40, 40), (panel_x, panel_y, panel_w, panel_h), 3)

    # Top and bottom rails
    pygame.draw.line(screen, (120, 120, 120), (panel_x, panel_y), (panel_x + panel_w, panel_y), 8)
    pygame.draw.line(screen, (120, 120, 120), (panel_x, panel_y + panel_h), (panel_x + panel_w, panel_y + panel_h), 8)

    # Cables
    car_center_x_int = int(car_x + car_w // 2)
    pygame.draw.line(screen, (230, 230, 230), (car_center_x_int, panel_y), (car_center_x_int, int(car_y)), 2)
    pygame.draw.line(screen, (230, 230, 230), (car_center_x_int, int(car_y + car_h)), (car_center_x_int, panel_y + panel_h), 2)

    # Carriage
    pygame.draw.rect(screen, (180, 220, 255), (int(car_x), int(car_y), car_w, car_h))
    pygame.draw.rect(screen, (60, 90, 120), (int(car_x), int(car_y), car_w, car_h), 2)

    # Draw target point
    pygame.draw.circle(screen, (255, 80, 80), (int(target_x), int(target_y)), 5)

    info = [
        f"Position: x={int(car_x - panel_x)}, y={int(car_y - panel_y)}",
        f"Target: x={int(target_x - panel_x)}, y={int(target_y - panel_y)}",
    ]

    y_text = 20
    for line in info:
        surf = font.render(line, True, (20, 20, 20))
        screen.blit(surf, (20, y_text))
        y_text += 30

    pygame.display.flip()

pygame.quit()
sys.exit()