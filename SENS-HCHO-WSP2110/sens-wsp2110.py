from machine import ADC, Pin
import math
import time

# Constants
Vc = 4.95  # Operating voltage
R0 = 34.28  # Base resistance (you'll need to calibrate this value)

# Setup ADC on pin A0 (adjust pin number according to your board)
adc = ADC(Pin(33))  # Use appropriate pin number for your board
adc.atten(ADC.ATTN_11DB)  # Full range: 3.3v

def calculate_ppm():
    # Read analog value
    sensor_value = adc.read()
    
    # Convert to 0-1023 range (similar to Arduino's 10-bit ADC)
    sensor_value = int((sensor_value / 65535) * 1023)
    
    # Calculate Rs (sensor resistance)
    Rs = (1023.0 / sensor_value) - 1
    
    # Calculate HCHO concentration in ppm
    # Using the formula: ppm = 10^((log10(Rs/R0) - 0.0827) / (-0.4807))
    try:
        ppm = pow(10.0, ((math.log10(Rs/R0) - 0.0827) / (-0.4807)))
        return Rs, ppm
    except ValueError:
        return Rs, 0

def calibrate_sensor():
    """
    Calibration function to determine R0
    Run this in clean air to get the R0 value
    """
    print("Calibrating sensor...")
    readings = []
    for _ in range(10):
        sensor_value = adc.read()
        sensor_value = int((sensor_value / 65535) * 1023)
        R0 = (1023.0 / sensor_value) - 1
        readings.append(R0)
        time.sleep(1)
    
    # Return average R0
    return sum(readings) / len(readings)

from M5 import Display

def main():
    # Uncomment the following lines to perform calibration
    # R0 = calibrate_sensor()
    # print(f"Calibrated R0 value: {R0}")
    display = Display()

    while True:
        try:
            Rs, ppm = calculate_ppm()
            rstr = f"Rs = {Rs:.2f}"
            ppmstr = f"HCHO ppm = {ppm:.2f}"
            print(rstr)
            print(ppmstr)
            print("-" * 20)
            display.show_message_list([rstr,ppmstr])
            time.sleep(1)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
