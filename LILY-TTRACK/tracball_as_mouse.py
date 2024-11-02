#circuitpython

import board
import digitalio
import usb_hid
from adafruit_hid.mouse import Mouse
from time import sleep

# Initialize the mouse
mouse = Mouse(usb_hid.devices)

# Set up trackball pins
gs1 = digitalio.DigitalInOut(board.IO1)  # Left
gs1.direction = digitalio.Direction.INPUT
gs1.pull = digitalio.Pull.DOWN

gs2 = digitalio.DigitalInOut(board.IO2)  # Down
gs2.direction = digitalio.Direction.INPUT
gs2.pull = digitalio.Pull.DOWN

gs3 = digitalio.DigitalInOut(board.IO3)  # Right
gs3.direction = digitalio.Direction.INPUT
gs3.pull = digitalio.Pull.DOWN

gs4 = digitalio.DigitalInOut(board.IO10)  # Up
gs4.direction = digitalio.Direction.INPUT
gs4.pull = digitalio.Pull.DOWN

gs0 = digitalio.DigitalInOut(board.IO0)  # Up
gs0.direction = digitalio.Direction.INPUT
gs0.pull = digitalio.Pull.UP

# Movement settings
MOVE_DISTANCE = 15  # Adjust this value to change sensitivity
DELAY = 0.001      # Adjust this value to change response speed

# Previous states
prev_states = {
    'left': False,
    'right': False,
    'up': False,
    'down': False,
    'key': True
}

while True:
    x = 0
    y = 0
    k = False
    
    # Current states
    curr_states = {
        'left': gs1.value,
        'right': gs3.value,
        'up': gs4.value,
        'down': gs2.value,
        'key': gs0.value
    }
    
    # Check for state changes and move accordingly
    if curr_states['left'] != prev_states['left'] and curr_states['left']:
        x = -MOVE_DISTANCE
    if curr_states['right'] != prev_states['right'] and curr_states['right']:
        x = MOVE_DISTANCE
    if curr_states['up'] != prev_states['up'] and curr_states['up']:
        y = -MOVE_DISTANCE
    if curr_states['down'] != prev_states['down'] and curr_states['down']:
        y = +MOVE_DISTANCE
    if curr_states['key'] != prev_states['key']:
        k = not curr_states['key']
        
        
    # Move mouse if there's any input
    if x != 0 or y != 0:
        mouse.move(x=x, y=y)
    if k:
        mouse.click(Mouse.LEFT_BUTTON)
    
    # Update previous states
    prev_states = curr_states.copy()
    sleep(DELAY)