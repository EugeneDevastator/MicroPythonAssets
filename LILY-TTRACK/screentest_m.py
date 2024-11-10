from machine import Pin, SPI
import time
import JD9613
import framebuf

from machine import mem32

pinPWR = Pin(4, Pin.OUT)
pinPWR.on()

# Use it like this:


def print_pin_states():
    states = {name: pin.value() for name, pin in pins.items()}
    print("Pin states:", states)
    
    # Also print raw binary states for debugging
    binary = "".join(str(x) for x in states.values())
    print(f"Binary: {binary}")
    
# Font constants
FONT_HEIGHT = 8
FONT_WIDTH = 8

# Configure SPI bus
spi = SPI(1, baudrate=80000000, polarity=0, phase=0, sck=Pin(5), mosi=Pin(6))

# Configure display pins
tft_cs = Pin(9, Pin.OUT)
tft_dc = Pin(7, Pin.OUT)
tft_reset = Pin(8, Pin.OUT)
#tft_bl = Pin(10, Pin.OUT) #backlight with same pin as trackball
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

# Cursor properties
CURSOR_SIZE = 3
CURSOR_COLOR = 0xFFFF  # White
BG_COLOR = 0x0000  # Black

def bl_on():
    backlight = Pin(10, Pin.OUT)
    backlight.value(1)
    pin10 = Pin(10, Pin.IN)

def reset_display():
    time.sleep_ms(100)
    tft_reset.value(0)
    time.sleep_ms(100)
    tft_reset.value(1)
    time.sleep_ms(100)
    
def read_display_status():
    send_command(0x09)  # RDDST command
    status = bytearray(4)
    tft_dc.value(1)
    tft_cs.value(0)
    spi.readinto(status)
    tft_cs.value(1)
    return status

def read_display_power_mode():
    send_command(0x0A)  # RDDPM command
    power_mode = bytearray(1)
    tft_dc.value(1)
    tft_cs.value(0)
    spi.readinto(power_mode)
    tft_cs.value(1)
    return power_mode[0]


def force_bright():
    #send_command(0x53) # control
    #send_data(0b0000000)	
    send_command(0x51)
    send_data(0xFF)
    
def software_reset():
    send_command(0x01)  # SWRESET command
 
def sleep_out():
    print("sleep out")

    send_command(0x11)
    time.sleep_ms(140)
    send_command(0x29)
    
def init_display():
    # Reset display
    tft_reset.value(0)
    time.sleep_ms(100)
    tft_reset.value(1)
    time.sleep_ms(100)

    # Initialize display
    for cmd in JD9613.CMD:
        #print(hex(cmd[0]))
        send_command(cmd[0])
        for param in cmd[1]:
            send_data(param)
        if cmd[2] & 0x80:
            time.sleep_ms(120)

    # Turn on backlight
    bl_on()
    #direct_pin_high(0)
    #force_bright()
    
    
def send_command(cmd):
    tft_dc.value(0)
    tft_cs.value(0)
    spi.write(bytes([cmd]))
    tft_cs.value(1)

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

def create_text_framebuf(text, color):
    buf_width = len(text) * FONT_WIDTH
    buf_height = FONT_HEIGHT
    buf = bytearray(buf_width * buf_height * 2)
    fb = framebuf.FrameBuffer(buf, buf_width, buf_height, framebuf.RGB565)
    fb.fill(0)
    fb.text(text, 0, 0, color)
    return fb

def draw_text(x, y, text, color):
    fb = create_text_framebuf(text, color)
    buf_width = len(text) * FONT_WIDTH
    buf_height = FONT_HEIGHT
    
    set_window(x, y, buf_width, buf_height)
    tft_dc.value(1)
    tft_cs.value(0)
    spi.write(fb)
    tft_cs.value(1)

def draw_scaled_text(x, y, text, color, scale=1):
    fb = create_text_framebuf(text, color)
    buf_width = len(text) * FONT_WIDTH
    buf_height = FONT_HEIGHT
    
    set_window(x, y, buf_width * scale, buf_height * scale)
    tft_dc.value(1)
    tft_cs.value(0)
    
    for row in range(buf_height):
        for _ in range(scale):
            for col in range(buf_width):
                pixel = fb.pixel(col, row)
                for _ in range(scale):
                    spi.write(bytes([pixel >> 8, pixel & 0xFF]))
    
    tft_cs.value(1)
    
class Cursor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.last_x = x
        self.last_y = y

    def draw(self):
        fill_rect(self.x, self.y, CURSOR_SIZE, CURSOR_SIZE, CURSOR_COLOR)

    def erase(self):
        fill_rect(self.last_x, self.last_y, CURSOR_SIZE, CURSOR_SIZE, BG_COLOR)

    def move(self, new_x, new_y):
        self.last_x = self.x
        self.last_y = self.y
        self.x = new_x
        self.y = new_y
# Initialize the display
#reset_display()

#software_reset()

# Set initial rotation (0 degrees)


#    set_rotation(rotation)
#    fill_rect(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, 0x001F)  # Blue background
#    fill_rect(20, 20, DISPLAY_WIDTH - 40, DISPLAY_HEIGHT - 40, 0xFFE0)  # Yellow rectangle

# Main loop
def main():
    init_display()
    set_rotation(ROTATION_0)
    tft_bl = Pin(10, Pin.IN, Pin.PULL_UP)
    force_bright()
    #tft_bl.value(1)
    status = read_display_status()
    print(f"Display Status: {status}")
    sleep_out()
    status = read_display_status()
    print(f"Display Status: {status}")
    
    power_mode = read_display_power_mode()
    print(f"Display Power Mode: {power_mode:08b}")
    
    print("rect filling")
    fill_rect(0, 50, DISPLAY_WIDTH, DISPLAY_HEIGHT, 0x01E0)
    # Test the display by drawing some rectangles
    #fill_rect(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, 0x07E0)  # Green background
    #fill_rect(20, 20, DISPLAY_WIDTH - 40, DISPLAY_HEIGHT - 40, 0xF800)  # Red rectangle
    # Example usage
    print("outing text")
    draw_text(10, 10, "Hello, World!", 0xFFFF)  # White text
    draw_text(10, 30, "LilyGo T-Track", 0xF800)  # Red text
    time.sleep(2)
    print("outing rect")
    fill_rect(0, 50, DISPLAY_WIDTH, DISPLAY_HEIGHT, 0x07E0)  # Green background
    # Rotate the display and draw more rectangles
    cursor = Cursor(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2)

    # Clear screen
    #fill_rect(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, BG_COLOR)
    print("entering loop")
    while True:
        #sleep_out()
        #print(tft_bl.value())
        force_bright()
        fill_rect(0, 50, 30, 30, 0x07E0)
        print("Pin state:", tft_bl.value())
        time.sleep(0.5)
        #status = read_display_status()
        #print(f"Display Status: {status}")
    while False:
        # Erase the cursor from its last position
        cursor.erase()

        # Move the cursor (example: move in a square pattern)
        if cursor.x < DISPLAY_WIDTH - CURSOR_SIZE and cursor.y == DISPLAY_HEIGHT // 2:
            cursor.move(cursor.x + 1, cursor.y)
        elif cursor.x == DISPLAY_WIDTH - CURSOR_SIZE and cursor.y < DISPLAY_HEIGHT - CURSOR_SIZE:
            cursor.move(cursor.x, cursor.y + 1)
        elif cursor.x > 0 and cursor.y == DISPLAY_HEIGHT - CURSOR_SIZE:
            cursor.move(cursor.x - 1, cursor.y)
        else:
            cursor.move(cursor.x, cursor.y - 1)

        # Draw the cursor at its new position
        cursor.draw()

        # Small delay to control the speed of movement
        time.sleep(0.1)

# Run the main loop
main()




