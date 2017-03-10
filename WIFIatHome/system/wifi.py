import network
import time

class wifi(object):

    def __init__(self,config):

        self._user = config.get('ESSID')
        self._passwd = config.get('PASSWD')

    def connect(self):
        nic = network.WLAN(network.STA_IF)
        print('Scan Networks', nic.scan())
        for i in range(3):
            if not nic.isconnected():
                nic.active(True)
                nic.connect(self._ssid, self._passwd)
                time.sleep(3)
            else:
                print('network config:', sta_if.ifconfig())
                return True

        return False


