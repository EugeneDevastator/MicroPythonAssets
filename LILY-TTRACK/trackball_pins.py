from machine import Pin, SPI
from time import sleep_ms

# Try different pin configurations
pins = {
    'gs1': Pin(1, Pin.IN, Pin.PULL_DOWN),  # Try PULL_DOWN instead of PULL_UP
    'gs2': Pin(2, Pin.IN, Pin.PULL_DOWN),
    'gs3': Pin(3, Pin.IN, Pin.PULL_DOWN),
    'gs4': Pin(10, Pin.IN, Pin.PULL_DOWN),
    'gsKey': Pin(0, Pin.IN, Pin.PULL_DOWN)
}

def print_pin_states():
    states = {name: pin.value() for name, pin in pins.items()}
    print("Pin states:", states)
    
    # Also print raw binary states for debugging
    binary = "".join(str(x) for x in states.values())
    print(f"Binary: {binary}")

# Monitoring loop with more verbose output
while True:
    print_pin_states()
    sleep_ms(100)  # Slower update for readability