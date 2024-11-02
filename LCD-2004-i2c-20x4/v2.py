from machine import I2C, Pin
import time

class LCD_I2C:
    # PCF8574 pin definitions
    MASK_RS = 0x01       # P0
    MASK_RW = 0x02       # P1
    MASK_E  = 0x04       # P2
    MASK_BL = 0x08       # P3
    MASK_D4 = 0x10       # P4
    MASK_D5 = 0x20       # P5
    MASK_D6 = 0x40       # P6
    MASK_D7 = 0x80       # P7

    def __init__(self, i2c, rows=4, cols=20):
        self.i2c = i2c
        self.rows = rows
        self.cols = cols
        self.lines = [0x80, 0xC0, 0x94, 0xD4]
        
        # Detect I2C address
        self.scan_result = i2c.scan()
        if not self.scan_result:
            raise Exception("No I2C device found")
        self.address = self.scan_result[0]
        print(f"Found LCD at address: 0x{self.address:x}")
        
        self.backlight = True
        time.sleep_ms(100)  # Wait after power on
        self._init_display()

    def _pulse_enable(self, data):
        # Pulse the enable pin
        self._write_raw(data | self.MASK_E)  # Enable high
        time.sleep_us(500)                    # Enable pulse width
        self._write_raw(data & ~self.MASK_E)  # Enable low
        time.sleep_us(100)                    # Enable cycle time

    def _write_raw(self, data):
        if self.backlight:
            data |= self.MASK_BL
        else:
            data &= ~self.MASK_BL
        try:
            self.i2c.writeto(self.address, bytes([data]))
        except Exception as e:
            print(f"Write error: {e}")

    def _write_4bits(self, data, rs=False):
        # Prepare data bits
        bits_high = data & 0xF0  # High nibble first
        bits_low = (data << 4) & 0xF0  # Low nibble second
        
        # Add RS bit
        if rs:
            bits_high |= self.MASK_RS
            bits_low |= self.MASK_RS
        
        # Send both nibbles
        self._pulse_enable(bits_high)
        self._pulse_enable(bits_low)

    def _write_cmd(self, cmd):
        self._write_4bits(cmd, rs=False)
        time.sleep_ms(2)  # Most commands need 1.52ms
    
    def _write_data(self, data):
        self._write_4bits(data, rs=True)
        time.sleep_us(100)  # Data needs 43us
    
    def _init_display(self):
        print("Initializing display...")
        
        # Initial 8-bit mode initialization
        for i in range(3):
            self._write_raw(0x30)
            self._pulse_enable(0x30)
            time.sleep_ms(5)
        
        # Switch to 4-bit mode
        self._write_raw(0x20)
        self._pulse_enable(0x20)
        time.sleep_ms(5)
        
        # Function set: 4-bit mode, 2 lines, 5x8 font
        self._write_cmd(0x28)
        
        # Display control: display on, cursor off, blink off
        self._write_cmd(0x0C)
        
        # Clear display and return home
        self.clear()
        
        # Entry mode set: Increment cursor, no display shift
        self._write_cmd(0x06)
        
        print("Initialization complete")

    def clear(self):
        """Clear the display"""
        self._write_cmd(0x01)
        time.sleep_ms(2)
    
    def home(self):
        """Return cursor to home position"""
        self._write_cmd(0x02)
        time.sleep_ms(2)
    
    def move_to(self, row, col):
        """Move cursor to specified position"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self._write_cmd(self.lines[row] + col)
    
    def write_string(self, string):
        """Write string at current cursor position"""
        for char in string:
            self._write_data(ord(char))
    
    def display_text(self, text, row=0, col=0):
        """Display text at specified position"""
        self.move_to(row, col)
        self.write_string(text[:self.cols])

# Test code
def test_lcd():
    print("Starting LCD test...")
    i2c = I2C(0, sda=Pin(26), scl=Pin(0), freq=100000)
    
    try:
        lcd = LCD_I2C(i2c)
        
        # Simple test pattern
        print("Writing test pattern...")
        lcd.clear()
        time.sleep_ms(100)
        
        # Test one line at a time with delays
        test_lines = [
            "Test Line 1",
            "Hello Line 2",
            "Testing 3",
            "Last Line 4"
        ]
        
        for i, line in enumerate(test_lines):
            print(f"Writing line {i+1}: {line}")
            lcd.display_text(line, i, 0)
            time.sleep_ms(500)
        
        print("Test complete")
        
    except Exception as e:
        print(f"Error during test: {e}")

# Run the test
test_lcd()