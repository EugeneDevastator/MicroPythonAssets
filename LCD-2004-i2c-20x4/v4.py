from machine import I2C, Pin
import time

class LCD_I2C:
    # Alternative PCF8574T pin mapping
    P0 = 0x01  # RS
    P1 = 0x02  # RW
    P2 = 0x04  # EN
    P3 = 0x08  # LED
    P4 = 0x10  # D4
    P5 = 0x20  # D5
    P6 = 0x40  # D6
    P7 = 0x80  # D7

    def __init__(self, i2c, address=0x27):
        self.i2c = i2c
        self.address = address
        self.backlight = True
        print(f"Initializing LCD at address 0x{address:x}")
        
        # Store current data
        self._data = 0x00
        
        time.sleep_ms(100)
        self._init_sequence()

    def _write_i2c(self, byte):
        if self.backlight:
            byte |= self.P3
        try:
            self.i2c.writeto(self.address, bytes([byte]))
            time.sleep_us(50)
        except Exception as e:
            print(f"I2C Write Error: {e}")

    def _write_4bits(self, value, rs=False):
        # Prepare data
        data = value & 0xF0  # Get high 4 bits
        if rs:
            data |= self.P0  # Set RS bit for data
        if self.backlight:
            data |= self.P3  # Set backlight
            
        # Write sequence with enable pulse
        self._write_i2c(data)
        self._write_i2c(data | self.P2)  # Set EN high
        time.sleep_us(1)
        self._write_i2c(data)            # Set EN low
        time.sleep_us(50)

    def _write_byte(self, value, rs=False):
        # Write high 4 bits
        self._write_4bits(value, rs)
        # Write low 4 bits
        self._write_4bits(value << 4, rs)
        time.sleep_us(50)

    def _init_sequence(self):
        print("Starting initialization sequence...")
        
        # Wait for more than 40ms after power up
        time.sleep_ms(50)
        
        # Initialize 8-bit mode first
        print("Setting up 8-bit mode...")
        for _ in range(3):
            self._write_4bits(0x30)
            time.sleep_ms(5)
        
        # Set 4-bit mode
        print("Switching to 4-bit mode...")
        self._write_4bits(0x20)
        time.sleep_ms(5)
        
        # Now configure the LCD
        print("Configuring display...")
        commands = [
            0x28,  # Function set: 4-bit mode, 2 lines, 5x8 dots
            0x0C,  # Display control: Display ON, cursor OFF, blink OFF
            0x06,  # Entry mode: Increment cursor, no display shift
            0x01   # Clear display
        ]
        
        for cmd in commands:
            self._write_byte(cmd)
            time.sleep_ms(2)
        
        print("Initialization complete")

    def clear(self):
        self._write_byte(0x01)  # Clear display
        time.sleep_ms(2)

    def write_char(self, char):
        self._write_byte(ord(char), rs=True)

    def write_string(self, string):
        for char in string:
            self.write_char(char)

    def set_cursor(self, line, column):
        offsets = [0x00, 0x40, 0x14, 0x54]  # Line offsets for 20x4 LCD
        if 0 <= line <= 3 and 0 <= column <= 19:
            self._write_byte(0x80 | (offsets[line] + column))
            time.sleep_ms(1)

def test_display():
    print("Setting up I2C...")
    sda = Pin(26, Pin.PULL_UP)
    scl = Pin(0, Pin.PULL_UP)
    i2c = I2C(0, sda=sda, scl=scl, freq=10000)
    
    print("Scanning I2C bus...")
    devices = i2c.scan()
    print(f"Found devices at: {[hex(x) for x in devices]}")
    
    if 0x27 not in devices:
        print("LCD not found at 0x27!")
        return
        
    try:
        print("Creating LCD object...")
        lcd = LCD_I2C(i2c)
        
        # First, try just initializing display and showing a single character
        print("Testing single character...")
        lcd.clear()
        time.sleep_ms(100)
        lcd.set_cursor(0, 0)
        lcd.write_char('X')
        time.sleep_ms(1000)
        
        # If that worked, try writing strings
        print("Testing full display...")
        test_strings = [
            "X123456789",  # First line
            "Testing...",  # Second line
            "ABCDEFGHIJ",  # Third line
            "<<TEST>>"     # Fourth line
        ]
        
        for i, text in enumerate(test_strings):
            print(f"Writing line {i}: {text}")
            lcd.set_cursor(i, 0)
            lcd.write_string(text)
            time.sleep_ms(500)
            
    except Exception as e:
        print(f"Error during test: {e}")
        raise e

print("Starting test...")
test_display()