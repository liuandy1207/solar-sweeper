# Solar Sweeper

Solar Sweeper is a mechatronics-based approach to cleaning solar panels involving a dual-axis cable-driven gantry system.

## Hardware Count
- 1 x Raspberry Pi Pico (w/ CircuitPython firmware)
- 2 x TMC2209 Motor Drivers w/ Breakout Boards
- 3 x Nema 17 Mini Stepper Motors
- 1 x Barrel Jack Adapter
- 1 x AC-DC Power Converter (12V 5A)
- Jumper Wires
- Breadboard

## Project Structure
```
solar-sweeper/
├── code.py                   # RPi Pico code for triggering movements by keyboard
├── keyboard_controls.py      # WASD keyboard input
├── pico_controller.py        # RPi Pico code for triggering movements by point-and-click
├── simulation_controller.py  # point-and-click input
└── README.md
```
