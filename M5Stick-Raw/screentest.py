import random
import machine
import time

import axp192
import colors
import pcf8563
import st7789

# Set up AXP192 PMU
i2c = machine.I2C(0, sda=machine.Pin(21), scl=machine.Pin(22), freq=400000)
pmu = axp192.AXP192(i2c, board=axp192.M5StickCPlus)
print("Battery Status: {:.2f} V".format(pmu.batt_voltage()))

# Set up BM8563 RTC (clone of the NXP PCF8563)
rtc = pcf8563.PCF8563(i2c)
print("Current Date and Time: {}".format(rtc.datetime()))

# Set up ST7789 TFT
spi = machine.SPI(1, baudrate=20_000_000, polarity=1,
                  sck=machine.Pin(13, machine.Pin.OUT),
                  miso=machine.Pin(4, machine.Pin.IN),  # NC
                  mosi=machine.Pin(15, machine.Pin.OUT))

tft = st7789.ST7789(spi, 135, 240,
                    reset=machine.Pin(18, machine.Pin.OUT),
                    dc=machine.Pin(23, machine.Pin.OUT),
                    cs=machine.Pin(5, machine.Pin.OUT),
                    buf=bytearray(2048))

c = colors.rgb565(
    random.getrandbits(8),
    random.getrandbits(8),
    random.getrandbits(8),
)
tft.fill(c)
tft.text("Hello World", 10, 30, colors.WHITE, c)

# Set up button
button = machine.Pin(37, machine.Pin.IN)

# List of messages to cycle through
messages = [
    "Hello World",
    "Press Again!",
    "M5StickC Plus",
    "MicroPython Rules!"
]
current_message = 0

def clear_text_area(background_color):
    # Clear just the text area instead of the whole screen
    tft.fill_rect(0, 20, 240, 50, background_color)

def show_message():
    # Generate random background color
    c = colors.rgb565(
        random.getrandbits(8),
        random.getrandbits(8),
        random.getrandbits(8),
    )
    
    # Clear screen with new color
    clear_text_area(c)
    
    # Display new message
    tft.text(messages[current_message], 10, 30, colors.WHITE, c)

# Initial display
show_message()

# Main loop
while True:
    if not button.value():  # Button is pressed (active low)
        # Update message index
        current_message = (current_message + 1) % (len(messages)-1)
        show_message()
        # Debounce
        time.sleep(0.2)