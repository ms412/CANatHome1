import pyb
from machine import Pin


class output(object):
    def __init__(self,name,config,callback):
       # mode = config.get('MODE', 'OUTPUT')
        port = config.get('PORT', 1)
        self._name = name
        self._callback = callback
        print('GPIO-output',port,config,name,callback)

        self._gpio = Pin(port, Pin.OUT)

    def run(self):
        while True:

            yield

    def SET(self,value):
        if 'ON' in value:
           self._gpio.value(1)
        else:
           self._gpio.value(0)
           #self._gpio.off()
     #   print('GET METHode VALUE',value)
        return True

class input(object):
    def __init__(self,name,config,callback):
        port = config.get('PORT', 1)
        self._name = name
        self._callback = callback

        self.name = name
        self._save = False
     #   print('GPIO-input', port, config, name, callback)
        self._pin = pyb.Pin(port, pyb.Pin.IN, pyb.Pin.PULL_UP)
        self.msg ={}

        self._sinkList = config.get('SINK',None)


    def call(self,data):
        if 0 == data:
            temp = 'OFF'
        else:
            temp = 'ON'

        for sinkMsg in self._sinkList:
            sinkMsg['VALUE'] = temp
            self._callback(sinkMsg)


    def run(self):
        self._save = self._pin.value()
       # print('START',self._save)
        self.call(self._save)
        while True:
            temp = self._pin.value()
            if temp != self._save:
        #        print('TEST',self._pin.value())
                self.call(temp)
                #self.callback('456')
                self._save = temp
            yield