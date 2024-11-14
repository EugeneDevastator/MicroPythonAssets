# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
#import screentest_m
#screentest_m.main()


from machine import Pin
pinPWR = Pin(4, Pin.OUT)
pinPWR.on()

import screentest_m