from machine import ADC, Pin
import time

# Configure ADC for battery monitoring
# Use appropriate ADC pin based on your board's schematic
battery_adc = ADC(Pin(1)) # Replace with correct pin number
battery_adc.atten(ADC.ATTN_11DB) # For 0-3.3V range
#battery_adc.width(ADC.WIDTH_12BIT)

def read_battery_voltage():
    # Read raw value and convert to voltage
    raw = battery_adc.read()
    voltage = raw * 3.3 / 4095  # Convert to voltage
    return voltage

def get_string():
    voltage = read_battery_voltage()
    percentage = ((voltage - 3.3) / (4.2 - 3.3)) * 100  # Approximate percentage
    percentage = max(0, min(100, percentage))  # Clamp between 0-100
    
    return f"{voltage:.2f}V {percentage:.1f}%"

def Test():
    while True:
        voltage = read_battery_voltage()
        percentage = ((voltage - 3.3) / (4.2 - 3.3)) * 100  # Approximate percentage
        #percentage = max(0, min(100, percentage))  # Clamp between 0-100
        
        print(f"Battery Voltage: {voltage:.2f}V")
        print(f"Battery Percentage: {percentage:.1f}%")
        time.sleep(1)

