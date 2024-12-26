to get 5v out use this code:
it will turn screen on tho
```py
import random
import machine
import time

import axp192
import colors
import pcf8563
import st7789

i2c = machine.I2C(0, sda=machine.Pin(21), scl=machine.Pin(22), freq=400000)
pmu = axp192.AXP192(i2c, board=axp192.M5StickCPlus)
```


todo: get expanded driver here:
https://github.com/russhughes/st7789_mpy