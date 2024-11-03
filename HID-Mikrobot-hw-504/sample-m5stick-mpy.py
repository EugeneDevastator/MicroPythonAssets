from machine import Pin, ADC
from time import sleep
import machine
import time

import axp192

# Set up AXP192 PMU for m5stick
i2c = machine.I2C(0, sda=machine.Pin(21), scl=machine.Pin(22), freq=400000)
pmu = axp192.AXP192(i2c, board=axp192.M5StickCPlus) 

# Setup analog pins for X and Y
vrx = ADC(Pin(26))
vry = ADC(Pin(25))

# Setup switch pin with pull-up resistor
sw = Pin(0, Pin.IN, Pin.PULL_UP)

# Configure ADC for proper voltage range (0-3.3V)
vrx.atten(ADC.ATTN_11DB)
vry.atten(ADC.ATTN_11DB)

while True:
    # Read values
    x_value = vrx.read()
    y_value = vry.read()
    switch_value = not sw.value()  # Inverted because of pull-up
    
    # Print values
    print(f"X: {x_value}, Y: {y_value}, Switch: {'Pressed' if switch_value else 'Released'}")
    
    sleep(0.1)  # Small delay to make output readable