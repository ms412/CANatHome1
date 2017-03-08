import utime
import ujson

from machine import WDT

class heardbeat(object):
    def __init__(self,config,callback):
        print('System',config)
        # mode = config.get('MODE', 'OUTPUT')
        self._interval = config.get('INTERVAL', 30)
        self._canId = config.get('CAN-ID')
        self._systemId = config.get('SYSTEM-ID')
   #     self._name = name
        self._callback = callback
        print(utime.time())
       # self._msg = {}

    def call(self):
        msg = {}
        value = {}
        msg['OBJECT']='HEARDBEAT'
        msg['METHOD'] = 'NULL'
        value['TIME']=utime.time()
        msg['CAN-ID'] = self._canId
        value['SYSTEM-ID'] = self._systemId
        msg['VALUE']=ujson.dumps(value)
        self._callback(msg)

    def run(self):
       # self._save = self._pin.value()
        # print('START',self._save)
        #self.call(self._save)
        while True:
            self.call()
         #   temp = self._pin.value()
          #  if temp != self._save:
                #        print('TEST',self._pin.value())d
           #     self.call(temp)
                # self.callback('456')
            #    self._save = temp
            yield self._interval


class watchdog(object):
    def __init__(self,wdtimeout):
        #self._wdtimeout = wdtimeout+30000
        print('Timeout', wdtimeout)
        self._watchdog = WDT(timeout=wdtimeout)

    def run(self):
        while True:
            self._watchdog.feed()
            print('reset timeout')
            yield 2
