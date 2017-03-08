from pyb import CAN
import array
import utime
import ujson


class canIf(object):
    def __init__(self,canId = 1):
   #     self._canIf = CAN(1, CAN.NORMAL, extframe=False, prescaler=16, sjw=1, bs1=14, bs2=6)
   #     self._canIf.setfilter(0, CAN.LIST16, 0, (124, 124, 124, 124))
        self._canIf = None
        self._canId = canId
        self._canAddr = 255

        self._rxTimeout = 5

      #  self._FRM_BYTE = 0x7D
       # self._ESC_BYTE = 0x7E

        self._txByte = 0
        self._rxByte = 0
        self._txFrame = 0
        self._rxFrame = 0

    def bitrate(self, bitrate = 125):
        if bitrate == 125:
            # 125kpbs, PCLK1@42000000
            self._canIf = CAN(self._canId, CAN.NORMAL, extframe=False, prescaler=16, sjw=1, bs1=14, bs2=6)
            print('set can speed', bitrate)
        elif bitrate == 250:
            ''' Init for 250 kbps <=> bit time 4 µs. If 42 MHz clk is prescaled by 21, we get 8 subparts 'tq'
            of a bit time from theese parts (# tq): sync(1) + bs1(5) + bs2(2) = 8 * tq = 4µs => 250 kbps'''
            self._canIf = CAN(self._canId, CAN.NORMAL, extframe=False, prescaler=21, sjw=1, bs1=5, bs2=2)
        else:
            print('CAN speed not found')

        self._canIf.initfilterbanks(1)
        return True

    def filter(self, address):
        canfilterList = []
        for x in range(0, 4):
            canfilterList.append(address)
            #  mylist.append(123)
        self._canAddr = address
        self._canIf.setfilter(0, CAN.LIST16, 0, canfilterList)
        print('Filter',self._canAddr)
        return True

    def any(self):
        self._canIf.any(0)

    def recv(self):
        self._canIf.recv(0)


    def send(self, buffer):
        # print('canSend',buffer)
        result = True
        try:
            self._canIf.send(buffer, self._canAddr, timeout=100)
            self._txByte += len(buffer)
            self._txFrame += 1
        except:
            result = False
            print('Failed to Send')

        return result