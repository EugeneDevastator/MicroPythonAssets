from machine import Pin
from neopixel import NeoPixel
import time

# Configuration
LED_PIN = 26
NUM_LEDS = 16
BUTTON_PIN = 37  # You can change this to your desired button pin

# Initialize NeoPixel strip
np = NeoPixel(Pin(LED_PIN), NUM_LEDS)
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)

# Color definitions
FULL_WHITE = (255, 255, 250)  # Full power white
WARM_WHITE = (255, 200, 100)  # Warm white
HALF_WHITE = (128, 128, 120)  # Half power white
HALF_WARM = (128, 100, 50)   # Half power warm white

# Mode management
current_mode = 0
modes = [
    ("FULL POWER", FULL_WHITE),
    ("FULL POWER WARM", WARM_WHITE),
    ("HALF POWER", HALF_WHITE),
    ("HALF POWER WARM", HALF_WARM)
]

def set_all_leds(color):
    """Set all LEDs to the specified color"""
    for i in range(NUM_LEDS):
        np[i] = color
    np.write()

def clear_all():
    """Turn off all LEDs"""
    set_all_leds((0, 0, 0))

def change_mode():
    """Change to the next mode"""
    global current_mode
    current_mode = (current_mode + 1) % (len(modes)-1)
    mode_name, color = modes[current_mode]
    print(f"Mode: {mode_name}")
    set_all_leds(color)

# Button debouncing variables
last_button_time = 0
debounce_delay = 200  # milliseconds

def handle_button():
    """Handle button press with debouncing"""
    global last_button_time
    current_time = time.ticks_ms()
    if time.ticks_diff(current_time, last_button_time) > debounce_delay:
        if not button.value():  # Button is pressed (active low)
            change_mode()
            last_button_time = current_time

def main():
    """Main program loop"""
    # Initial setup
    clear_all()
    change_mode()
    
    # Main loop
    while True:
        handle_button()
        time.sleep_ms(50)  # Small delay to prevent busy waiting

try:
    main()
except KeyboardInterrupt:
    print("Program terminated")