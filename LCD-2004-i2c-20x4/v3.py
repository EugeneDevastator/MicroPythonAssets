from machine import I2C, Pin
import time

class LCD_I2C:
    # PCF8574T pin mapping (might be different from standard PCF8574)
    MASK_RS = 0x01
    MASK_RW = 0x02
    MASK_E  = 0x04
    MASK_BL = 0x08
    MASK_D4 = 0x10
    MASK_D5 = 0x20
    MASK_D6 = 0x40
    MASK_D7 = 0x80

    def __init__(self, i2c, rows=4, cols=20):
        self.i2c = i2c
        self.rows = rows
        self.cols = cols
        self.lines = [0x80, 0xC0, 0x94, 0xD4]
        self.backlight = True
        
        # Detect I2C address
        self.scan_result = i2c.scan()
        print(f"I2C scan results: {[hex(x) for x in self.scan_result]}")
        if not self.scan_result:
            raise Exception("No I2C device found")
        self.address = self.scan_result[0]
        print(f"Using LCD at address: 0x{self.address:x}")
        
        # Initial wait after power on
        time.sleep_ms(500)
        self._init_display()

    def _write(self, data):
        if self.backlight:
            data |= self.MASK_BL
        try:
            self.i2c.writeto(self.address, bytes([data]))
            time.sleep_us(50)
        except Exception as e:
            print(f"Write error: {e}")

    def _send(self, data, mode=0):
        # Mode: 0 for command, 1 for data
        high_nibble = data & 0xF0
        low_nibble = (data << 4) & 0xF0
        
        # Send high nibble
        self._write(high_nibble | mode)
        self._write(high_nibble | self.MASK_E | mode)  # Enable high
        self._write(high_nibble | mode)                # Enable low
        
        # Send low nibble
        self._write(low_nibble | mode)
        self._write(low_nibble | self.MASK_E | mode)  # Enable high
        self._write(low_nibble | mode)                # Enable low

    def _init_display(self):
        print("Starting display initialization...")
        
        # Reset sequence
        time.sleep_ms(50)
        init_sequence = [0x03, 0x03, 0x03, 0x02]
        
        for cmd in init_sequence:
            self._write((cmd << 4))
            self._write((cmd << 4) | self.MASK_E)
            time.sleep_ms(5)
            self._write((cmd << 4))
            time.sleep_ms(5)
        
        # Now configure the LCD
        init_commands = [
            0x28,  # Function set: 4-bit mode, 2 lines, 5x8 dots
            0x08,  # Display off
            0x01,  # Clear display
            0x06,  # Entry mode set: increment cursor, no shift
            0x0C   # Display on, cursor off, blink off
        ]
        
        for cmd in init_commands:
            self._send(cmd)
            time.sleep_ms(5)
            
        print("Initialization complete")

    def clear(self):
        self._send(0x01)  # Clear display
        time.sleep_ms(5)

    def home(self):
        self._send(0x02)  # Return home
        time.sleep_ms(5)

    def move_to(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self._send(self.lines[row] + col)
            time.sleep_ms(1)

    def write_char(self, char):
        self._send(ord(char), mode=self.MASK_RS)
        time.sleep_ms(1)

    def write_string(self, string):
        for char in string:
            self.write_char(char)

    def display_text(self, text, row=0, col=0):
        self.move_to(row, col)
        self.write_string(text[:self.cols])

def test_lcd():
    print("Setting up I2C...")
    # Enable internal pullups for M5StickC
    sda_pin = Pin(26, Pin.PULL_UP)
    scl_pin = Pin(0, Pin.PULL_UP)
    # Try a lower frequency
    i2c = I2C(0, sda=sda_pin, scl=scl_pin, freq=10000)
    
    try:
        print("Creating LCD object...")
        lcd = LCD_I2C(i2c)
        
        # Test sequence
        print("Starting display test...")
        lcd.clear()
        time.sleep_ms(100)
        
        # Simple test pattern
        print("Writing test pattern...")
        patterns = [
            "1234",
            "ABCD",
            "Test",
            "Done"
        ]
        
        for i, text in enumerate(patterns):
            print(f"Writing line {i+1}: {text}")
            lcd.display_text(text, i, 0)
            time.sleep_ms(1000)  # Longer delay between lines
        
        print("Test complete")
        
    except Exception as e:
        print(f"Error during test: {e}")
        raise e

# Run the test
print("Starting program...")
test_lcd()