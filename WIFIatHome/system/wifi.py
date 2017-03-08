import network
import time

class wifi(object):

    def __init__(self,config):

        self._user = config.get('ESSID')
        self._passwd = config.get('PASSWD')

    def connect(self):
        sta_if = network.WLAN(network.STA_IF)
 #   sta_if = WLAN(network.STA_IF)
        print('Scan Networks', sta_if.scan())
        while not sta_if.isconnected():
            print('connecting to network...')
            sta_if.active(True)
            sta_if.connect(self._ssid, self._passwd)
            time.sleep(2)
       # while not sta_if.isconnected():
        #    pass
        print('network config:', sta_if.ifconfig())

