# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import machine
import gc
pin = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
if pin.value():
    print('ON')
    gc.collect()
else:
    print('OFF')
    import webrepl
    webrepl.start()
    gc.collect()
#import gc
#import webrepl
#webrepl.start()
#gc.collect()