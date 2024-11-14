from machine import Pin
import time

# First, initialize pin 10 as output and set it high (like display init does)
pin10 = Pin(10, Pin.OUT)
pin10.value(1)
pinPWR = Pin(4, Pin.OUT)
pinPWR.on()
# Then reconfigure for input with pull-down (matching your display code)
pin10.init(Pin.IN, Pin.PULL_DOWN)

# Now we can monitor the trackball input
while True:
    print("Pin state:", pin10.value())
    time.sleep(0.1)