from machine import Pin, SPI
from time import sleep_ms
# Try different pin configurations
pins = {
    'gs1': Pin(1, Pin.IN, Pin.PULL_DOWN),  # y down
    'gs2': Pin(2, Pin.IN, Pin.PULL_DOWN),  # x right
    'gs3': Pin(3, Pin.IN, Pin.PULL_DOWN),  # y up
    'gs4': Pin(10, Pin.IN, Pin.PULL_DOWN), # x left
    'gsKey': Pin(0, Pin.IN, Pin.PULL_UP),
}

def print_pin_states():
    states = {name: pin.value() for name, pin in pins.items()}
    print("Pin states:", states)
    
    # Also print raw binary states for debugging
    binary = "".join(str(x) for x in states.values())
    print(f"Binary: {binary}")
sleep_ms(200)
#p10.init(p10.OUT, value=1, drive=Pin.DRIVE_3)
# Monitoring loop with more verbose output
while True:

    #p10.on()
    print_pin_states()
    sleep_ms(100)  # Slower update for readability