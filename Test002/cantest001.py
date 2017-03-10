
from pyb import CAN, LED, delay
import array
import utime
import ujson


class canIf(object):
    def __init__(self,canPort = 1):
   #     self._canIf = CAN(1, CAN.NORMAL, extframe=False, prescaler=16, sjw=1, bs1=14, bs2=6)
   #     self._canIf.setfilter(0, CAN.LIST16, 0, (124, 124, 124, 124))
        self._canIf = None
        self._canPort = canPort


    def __del__(self):
        self._canIf.deinit()

    def bitrate(self, bitrate = 125):
        if bitrate == 125:
            # 125kpbs, PCLK1@42000000
            self._canIf = CAN(self._canPort, CAN.NORMAL, extframe=False, prescaler=16, sjw=1, bs1=14, bs2=6)
            print('set can speed', bitrate)
        elif bitrate == 250:
            ''' Init for 250 kbps <=> bit time 4 µs. If 42 MHz clk is prescaled by 21, we get 8 subparts 'tq'
            of a bit time from theese parts (# tq): sync(1) + bs1(5) + bs2(2) = 8 * tq = 4µs => 250 kbps'''
            self._canIf = CAN(self._canPort, CAN.NORMAL, extframe=False, prescaler=21, sjw=1, bs1=5, bs2=2)
        else:
            print('CAN speed not found')

        #self._canIf.initfilterbanks(14)
        return True

    def filter(self):

        self._canIf.setfilter(0, CAN.LIST16, 0, (11,12,13,14))
        self.rxcallback(0,self.callback)
        return True

    def callback(self):
        print('Rx', self._canIf.recv(0, timeout=5000))

if __name__ == '__main__':
    can=canIf()
    can.bitrate(125)
    filter()
    while True:
        delay(100)
