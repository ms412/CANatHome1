
from machine import Pin


class port(object):
    def __init__(self,p):
     #   self._pinNo = 2
      #  self._pin = PIN(self._pinNo, Pin.IN)
      #  pin_int = Pin(p, mode=Pin.IN, pull=Pin.PULL_DOWN)

        pin_int = Pin(p, mode=Pin.IN, pull=Pin.PULL_UP)
        pin_int.irq(trigger=Pin.IRQ_RISING, handler=self.callback)
        print('PORT setup')
       # p2 = Pin(2, Pin.IN)

    def callback(self,pin):
        print('Callback',pin)
       # print(pin.id())

