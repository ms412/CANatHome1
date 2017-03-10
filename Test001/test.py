
import network

from simple import MQTTClient

def do_connect():
#    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('laudanum.net', 'nd%aG9im')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

def mqtt_connect():

    c = MQTTClient("umqtt_client", "192.168.2.50")
    c.connect()
    c.publish(b"foo_topic", b"hello")
    c.disconnect()


if __name__ == '__main__':
    do_connect()
    mqtt_connect()