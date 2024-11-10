from machine import Pin, SPI
import time
import JD9613

# Configure SPI bus
spi = SPI(1, baudrate=80000000, polarity=0, phase=0, sck=Pin(5), mosi=Pin(6))

# Configure display pins
tft_cs = Pin(9, Pin.OUT)
tft_dc = Pin(7, Pin.OUT)
tft_reset = Pin(8, Pin.OUT)

tft_bl = Pin(10, Pin.OUT)
#force the pin
#tft_bl.init(tft_bl.OUT, value=1, drive=Pin.DRIVE_3)

# Display dimensions
DISPLAY_WIDTH = 126
DISPLAY_HEIGHT = 294

# Rotation constants
ROTATION_0 = 0
ROTATION_90 = 1
ROTATION_180 = 2
ROTATION_270 = 3

# Current rotation
current_rotation = ROTATION_0

# JD9613_CMD remains the same as in your original code

def init_display():
    # Reset display
    tft_reset.value(0)
    time.sleep(0.1)
    tft_reset.value(1)
    time.sleep(0.1)

    # Initialize display
    for cmd in JD9613.CMD:
        send_command(cmd[0])
        for param in cmd[1]:
            send_data(param)
        if cmd[2] & 0x80:
            time.sleep(0.12)

    # Turn on backlight
    tft_bl.value(1)

def send_command(cmd):
    tft_dc.value(0)
    tft_cs.value(0)
    spi.write(bytes([cmd]))
    tft_cs.value(1)

def force_bright():
    #send_command(0x53) # control
    #send_data(0b0000000)	
    send_command(0x51)
    send_data(0xFF)

def send_data(data):
    tft_dc.value(1)
    tft_cs.value(0)
    spi.write(bytes([data]))
    tft_cs.value(1)

def set_rotation(rotation):
    global current_rotation
    current_rotation = rotation % 4
    send_command(0x36)  # MADCTL
    if current_rotation == ROTATION_0:
        send_data(0x08)  # BGR
    elif current_rotation == ROTATION_90:
        send_data(0x68)  # MX | MV | BGR
    elif current_rotation == ROTATION_180:
        send_data(0xC8)  # MX | MY | BGR
    elif current_rotation == ROTATION_270:
        send_data(0xA8)  # MV | MY | BGR

def set_window(x, y, w, h):
    if current_rotation == ROTATION_90 or current_rotation == ROTATION_270:
        x, y, w, h = y, x, h, w

    send_command(0x2A)  # Column address set
    send_data(x >> 8)
    send_data(x & 0xFF)
    send_data((x + w - 1) >> 8)
    send_data((x + w - 1) & 0xFF)

    send_command(0x2B)  # Row address set
    send_data(y >> 8)
    send_data(y & 0xFF)
    send_data((y + h - 1) >> 8)
    send_data((y + h - 1) & 0xFF)

    send_command(0x2C)  # Memory write

def fill_rect(x, y, w, h, color):
    set_window(x, y, w, h)
    tft_dc.value(1)
    tft_cs.value(0)
    for _ in range(w * h):
        spi.write(bytes([color >> 8, color & 0xFF]))
    tft_cs.value(1)

# Initialize the display
init_display()

# Set initial rotation (0 degrees)
set_rotation(ROTATION_0)

# Test the display by drawing some rectangles
fill_rect(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, 0x07E0)  # Green background
tft_bl.init(tft_bl.IN, tft_bl.PULL_DOWN)

fill_rect(20, 20, DISPLAY_WIDTH - 40, DISPLAY_HEIGHT - 40, 0xF800)  # Red rectangle

# Rotate the display and draw more rectangles
for rotation in range(1):
    time.sleep(2)  # Wait for 2 seconds before changing rotation
    set_rotation(rotation)
    fill_rect(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, 0x001F)  # Blue background
    fill_rect(20, 20, DISPLAY_WIDTH - 40, DISPLAY_HEIGHT - 40, 0xFFE0)  # Yellow rectangle

while True:
    #pin10 = Pin(10, Pin.IN, Pin.PULL_UP)
    #time.sleep(0.5)
    #print(pin10.value())
    #tft_bl = Pin(10, Pin.OUT)
    #tft_bl.value(1)
    #tft_bl.init(Pin.IN, Pin.PULL_DOWN)
    #tft_bl.init(tft_bl.OUT, value=1, drive=Pin.DRIVE_3)
    print("bl:"+str(tft_bl.value())) # here it is always 0.
    force_bright()
    fill_rect(0, 0, 50, 50, 0x021F)
    time.sleep(3)
    pass



