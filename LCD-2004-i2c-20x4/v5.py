from machine import I2C, Pin
import time

class LCD_I2C:
    def __init__(self, i2c, address=0x27):
        self.i2c = i2c
        self.address = address
        
        # PCF8574 pin definitions (P7-P0)
        self.RS = 0x01  # Register select: 0=Command, 1=Data
        self.RW = 0x02  # Read/Write: 0=Write, 1=Read
        self.EN = 0x04  # Enable
        self.BL = 0x08  # Backlight
        self.D4 = 0x10
        self.D5 = 0x20
        self.D6 = 0x40
        self.D7 = 0x80
        
        self.CHR = 1  # Character mode
        self.CMD = 0  # Command mode
        
        time.sleep_ms(500)  # Wait for display to power up
        self._init()
    
    def _write(self, data, mode=0):
        """Write to the LCD in 4-bit mode."""
        high_bits = mode | (data & 0xF0) | self.BL
        low_bits = mode | ((data << 4) & 0xF0) | self.BL
        
        # High bits with enable
        self._i2c_write(high_bits)
        self._i2c_write(high_bits | self.EN)  # Enable high
        time.sleep_us(1)
        self._i2c_write(high_bits)            # Enable low
        time.sleep_us(100)
        
        # Low bits with enable
        self._i2c_write(low_bits)
        self._i2c_write(low_bits | self.EN)   # Enable high
        time.sleep_us(1)
        self._i2c_write(low_bits)             # Enable low
        time.sleep_us(100)

    def _i2c_write(self, data):
        try:
            self.i2c.writeto(self.address, bytes([data]))
            time.sleep_us(50)
        except Exception as e:
            print(f"I2C write error: {e}")

    def _init(self):
        """Initialize the LCD."""
        print("Initializing LCD...")
        
        # Wait for more than 40ms after power up
        time.sleep_ms(1000)
        
        # Initial write (8-bit mode)
        for _ in range(3):
            self._i2c_write(0x30)
            self._i2c_write(0x34)
            time.sleep_ms(5)
            self._i2c_write(0x30)
            time.sleep_ms(5)
        
        # Set 4-bit mode
        self._i2c_write(0x20)
        self._i2c_write(0x24)
        time.sleep_ms(5)
        self._i2c_write(0x20)
        time.sleep_ms(5)
        
        # Function set: 4-bit mode, 2 lines, 5x8 dots
        self._write(0x28, self.CMD)
        time.sleep_ms(5)
        
        # Display control: Display on, cursor off, blink off
        self._write(0x0C, self.CMD)
        time.sleep_ms(5)
        
        # Entry mode set: Increment cursor, no display shift
        self._write(0x06, self.CMD)
        time.sleep_ms(5)
        
        # Clear display
        self.clear()
        print("Initialization complete")

    def clear(self):
        """Clear the display."""
        self._write(0x01, self.CMD)
        time.sleep_ms(5)

    def home(self):
        """Return cursor to home position."""
        self._write(0x02, self.CMD)
        time.sleep_ms(5)

    def move_to(self, row, col):
        """Move cursor to specified position."""
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        if 0 <= row <= 3 and 0 <= col <= 19:
            self._write(0x80 | (row_offsets[row] + col), self.CMD)
            time.sleep_ms(1)

    def putchar(self, char):
        """Write a single character."""
        self._write(ord(char), self.CHR)
        time.sleep_ms(1)

    def putstr(self, text):
        """Write a string."""
        for char in text:
            self.putchar(char)

def test():
    print("Starting LCD test...")
    
    # Initialize I2C with explicit pullups
    sda = Pin(26, Pin.PULL_UP)
    scl = Pin(0, Pin.PULL_UP)
    i2c = I2C(0, sda=sda, scl=scl, freq=10000)  # Very slow frequency
    
    try:
        # Scan for devices
        devices = i2c.scan()
        print(f"Found I2C devices: {[hex(x) for x in devices]}")
        
        lcd = LCD_I2C(i2c)
        
        # Test sequence with long delays
        print("Starting display test sequence...")
        
        # Test 1: Single characters
        print("Test 1: Single characters")
        lcd.clear()
        time.sleep_ms(1000)
        lcd.move_to(0, 0)
        lcd.putchar('A')
        time.sleep_ms(1000)
        
        # Test 2: Contrast test pattern
        print("Test 2: Contrast test pattern")
        patterns = [
            "########--------####",  # Alternating pattern
            "XXXXXXXXXXXXXXXX----",  # Dense pattern
            "................----",  # Light pattern
            "0123456789ABCDEF----"   # Mixed pattern
        ]
        
        for i, pattern in enumerate(patterns):
            lcd.move_to(i, 0)
            lcd.putstr(pattern)
            time.sleep_ms(1000)
        
        print("Test complete - adjust contrast if no text is visible")
        
    except Exception as e:
        print(f"Test error: {e}")

print("Program start")
test()