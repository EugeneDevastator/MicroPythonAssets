# m5stick_display.py
import random
import machine
import time
import axp192
import colors
import pcf8563
import st7789

class Display:
    def __init__(self):
        # Add default font height and padding
        self.font_height = 13
        self.line_padding = 2
        # Set up I2C
        self.i2c = machine.I2C(0, sda=machine.Pin(21), scl=machine.Pin(22), freq=400000)
        
        # Set up PMU
        self.pmu = axp192.AXP192(self.i2c, board=axp192.M5StickCPlus)
        
        # Set up RTC
        self.rtc = pcf8563.PCF8563(self.i2c)
        
        # Set up SPI and Display
        self.spi = machine.SPI(1, baudrate=20_000_000, polarity=1,
                             sck=machine.Pin(13, machine.Pin.OUT),
                             miso=machine.Pin(4, machine.Pin.IN),
                             mosi=machine.Pin(15, machine.Pin.OUT))
        
        self.tft = st7789.ST7789(self.spi, 135, 240,
                                reset=machine.Pin(18, machine.Pin.OUT),
                                dc=machine.Pin(23, machine.Pin.OUT),
                                cs=machine.Pin(5, machine.Pin.OUT),
                                buf=bytearray(2048))
        
        # Set up button
        self.button = machine.Pin(37, machine.Pin.IN)
        
        # Initialize messages
        self.messages = [
            "Hello World",
            "Press Again!",
            "M5StickC Plus",
            "MicroPython Rules!"
        ]
        self.current_message = 0

    def get_battery_voltage(self):
        """Return current battery voltage"""
        return self.pmu.batt_voltage()

    def get_datetime(self):
        """Return current date and time"""
        return self.rtc.datetime()

    def clear_text_area(self, background_color):
        """Clear the text area of the display"""
        self.tft.fill_rect(0, 20, 240, 50, background_color)

    def show_message(self, message=None, x=10, y=30):
        """Display a message on the screen"""
        c = colors.rgb565(
            random.getrandbits(8),
            random.getrandbits(8),
            random.getrandbits(8),
        )
        self.clear_text_area(c)
        
        if message is None:
            message = self.messages[self.current_message]
        
        self.tft.text(message, x, y, colors.WHITE, c)
    def show_message_list(self, messages, start_y=20, background_color=None):
        """
        Display a list of messages vertically on the screen
        
        Args:
            messages (list): List of strings to display
            start_y (int): Starting Y position for the first message
            background_color: Optional background color (random if None)
        """
        if background_color is None:
            background_color = colors.rgb565(
                random.getrandbits(8),
                random.getrandbits(8),
                random.getrandbits(8),
            )
        
        # Clear the entire display area
        self.tft.fill_rect(0, start_y, 240, 135-start_y, background_color)
        
        # Calculate total height needed
        total_height = len(messages) * (self.font_height + self.line_padding)
        
        # Display each message
        current_y = start_y
        for message in messages:
            # Ensure message fits on screen
            if current_y + self.font_height > 135:
                break
                
            self.tft.text(message, 10, current_y, colors.WHITE, background_color)
            current_y += self.font_height + self.line_padding

    def next_message(self):
        """Switch to the next message in the rotation"""
        self.current_message = (self.current_message + 1) % len(self.messages)
        self.show_message()

    def run(self):
        """Main loop to handle button presses"""
        self.show_message()  # Show initial message
        
        while True:
            if not self.button.value():
                self.next_message()
                time.sleep(0.2)  # Debounce
