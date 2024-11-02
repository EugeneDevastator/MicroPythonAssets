from machine import I2C, Pin
import time

class LCD_I2C:
    # LCD Commands
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    # Flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02

    # Flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    # Flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00

    def __init__(self, i2c, rows=4, cols=20):
        self.i2c = i2c
        self.rows = rows
        self.cols = cols
        self.lines = [0x80, 0xC0, 0x94, 0xD4]  # Line addresses for 4x20 LCD
        
        # Try to detect I2C address
        self.scan_result = i2c.scan()
        if not self.scan_result:
            raise Exception("No I2C device found")
        self.address = self.scan_result[0]
        print(f"Found LCD at address: 0x{self.address:x}")
        
        # Initialization
        self.backlight = True
        self.displaycontrol = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
        self.displayfunction = self.LCD_4BITMODE | self.LCD_2LINE | self.LCD_5x8DOTS
        self.displaymode = self.LCD_ENTRYLEFT
        
        # Initialize display
        self._init_display()

    def _write_byte(self, data, rs=0):
        # Prepare data including backlight bit (bit 3)
        backlight = 0x08 if self.backlight else 0x00
        
        # Send data in two nibbles with RS and backlight bits
        upper_nibble = (data & 0xF0) | backlight | rs
        lower_nibble = ((data << 4) & 0xF0) | backlight | rs
        
        try:
            # Enable pulse for upper nibble (EN = 1)
            self.i2c.writeto(self.address, bytes([upper_nibble | 0x04]))
            time.sleep_us(100)
            self.i2c.writeto(self.address, bytes([upper_nibble & ~0x04]))
            time.sleep_us(100)
            
            # Enable pulse for lower nibble (EN = 1)
            self.i2c.writeto(self.address, bytes([lower_nibble | 0x04]))
            time.sleep_us(100)
            self.i2c.writeto(self.address, bytes([lower_nibble & ~0x04]))
            time.sleep_ms(1)
        except Exception as e:
            print(f"Write error: {e}")

    def _write_cmd(self, cmd):
        self._write_byte(cmd, rs=0)  # RS = 0 for commands
    
    def _write_data(self, data):
        self._write_byte(data, rs=1)  # RS = 1 for data
    
    def _init_display(self):
        print("Initializing display...")
        time.sleep_ms(50)  # Wait for LCD to power up
        
        # Initialize in 4-bit mode
        for i in range(3):  # Three attempts at 0x03
            self._write_cmd(0x03)
            time.sleep_ms(5)
        
        self._write_cmd(0x02)  # Finally set to 4-bit mode
        time.sleep_ms(1)
        
        # Function set: 4-bit mode, 2 lines, 5x8 font
        self._write_cmd(self.LCD_FUNCTIONSET | self.displayfunction)
        time.sleep_ms(1)
        
        # Display control: display on, cursor off, blink off
        self._write_cmd(self.LCD_DISPLAYCONTROL | self.displaycontrol)
        time.sleep_ms(1)
        
        # Clear display
        self.clear()
        
        # Entry mode set
        self._write_cmd(self.LCD_ENTRYMODESET | self.displaymode)
        time.sleep_ms(1)
        
        print("Initialization complete")
    
    def clear(self):
        """Clear the display"""
        self._write_cmd(self.LCD_CLEARDISPLAY)
        time.sleep_ms(2)
    
    def home(self):
        """Return cursor to home position"""
        self._write_cmd(self.LCD_RETURNHOME)
        time.sleep_ms(2)
    
    def move_to(self, row, col):
        """Move cursor to specified position"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self._write_cmd(self.lines[row] + col)
            time.sleep_ms(1)
    
    def write_string(self, string):
        """Write string at current cursor position"""
        for char in string:
            self._write_data(ord(char))
            time.sleep_ms(1)
    
    def display_text(self, text, row=0, col=0):
        """Display text at specified position"""
        self.move_to(row, col)
        self.write_string(text[:self.cols])

# Test code
def test_lcd():
    # Initialize I2C
    i2c = I2C(0, sda=Pin(26), scl=Pin(0), freq=100000)
    
    try:
        print("Starting LCD test...")
        lcd = LCD_I2C(i2c)
        
        # Test pattern
        test_text = [
            " ------------",
            " XXXXXXXXXXX",
            " <>?~!@#$%^&*()",
            " 1234567890-="
        ]
        
        print("Writing test pattern...")
        for i, text in enumerate(test_text):
            lcd.display_text(text, i, 0)
            time.sleep_ms(500)  # Delay between lines
            
        print("Test complete")
        
    except Exception as e:
        print(f"Error during test: {e}")

# Run the test
test_lcd()