from machine import ADC, Pin
import time

# voltage divider scheme: 3v3 -> 10kR ; 10kR + R2 -> ADC pin ; Gnd - R2 
# Configure ADC with attenuation
adc = ADC(Pin(13), atten=ADC.ATTN_11DB)
# Set 12-bit resolution (0-4095)
adc.width(ADC.WIDTH_12BIT)

R_REF = 10000  # 10k ohm reference resistor
V_SUPPLY = 3.3  # ESP32-S3 typically uses 3.3V

def measure_resistance():
    # Take multiple readings and average them
    samples = 10
    adc_value = 0
    for _ in range(samples):
        adc_value += adc.read()
        time.sleep(0.01)
    adc_value = adc_value / samples
    
    # Convert to voltage (12-bit ADC = 4096 steps)
    voltage = (adc_value / 4095) * V_SUPPLY
    print(f"ADC value: {adc_value:.0f}, Voltage: {voltage:.3f}V")
    
    if voltage >= V_SUPPLY:
        return 0
    if voltage <= 0:
        return float('inf')
    
    r_unknown = R_REF * (voltage / (V_SUPPLY - voltage))
    return r_unknown

while True:
    resistance = measure_resistance()
    print(f"Measured resistance: {resistance:.2f} ohms")
    time.sleep(1)
