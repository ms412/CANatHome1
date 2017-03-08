from machine import Pin
import onewire
import time, ds18x20



class onewire(object):
    def __init___(self,pin):
        self.ow = onewire.OneWire(pin)
        self.ds = ds18x20.DS18X20(self.ow)

    def oneWire(self):
        roms = self.ds.scan()
        self.ds.convert_temp()
        temp = 0
        for rom in roms:
            print(rom)
            temp = self.ds.read_temp(rom)
            print('temperatur',temp)

        return temp
