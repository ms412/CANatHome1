# https://github.com/Naish21/themostat
'''
 * The MIT License (MIT)
 *
 * Copyright (c) 2016 Jorge Aranda Moro
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.

'''

#This part is to connect to the WiFi
#In this case: SSID: TP-LINK_F3D4B2 & PASS: 90546747

import usocket as socket
import ustruct as struct
from ubinascii import hexlify
from port import port

class MQTTException(Exception):
    pass

class MQTTClient:

    def __init__(self, client_id, server, port=0, user=None, password=None, keepalive=0,
                 ssl=False, ssl_params={}):
        if port == 0:
            port = 8883 if ssl else 1883
        self.client_id = client_id
        self.sock = None
        self.addr = socket.getaddrinfo(server, port)[0][-1]
        self.ssl = ssl
        self.ssl_params = ssl_params
        self.pid = 0
        self.cb = None
        self.user = user
        self.pswd = password
        self.keepalive = keepalive
        self.lw_topic = None
        self.lw_msg = None
        self.lw_qos = 0
        self.lw_retain = False

    def _send_str(self, s):
        self.sock.write(struct.pack("!H", len(s)))
        self.sock.write(s)

    def _recv_len(self):
        n = 0
        sh = 0
        while 1:
            b = self.sock.read(1)[0]
            n |= (b & 0x7f) << sh
            if not b & 0x80:
                return n
            sh += 7

    def set_callback(self, f):
        self.cb = f

    def set_last_will(self, topic, msg, retain=False, qos=0):
        assert 0 <= qos <= 2
        assert topic
        self.lw_topic = topic
        self.lw_msg = msg
        self.lw_qos = qos
        self.lw_retain = retain

    def connect(self, clean_session=True):
        self.sock = socket.socket()
        self.sock.connect(self.addr)
        if self.ssl:
            import ussl
            self.sock = ussl.wrap_socket(self.sock, **self.ssl_params)
        msg = bytearray(b"\x10\0\0\x04MQTT\x04\x02\0\0")
        msg[1] = 10 + 2 + len(self.client_id)
        msg[9] = clean_session << 1
        if self.user is not None:
            msg[1] += 2 + len(self.user) + 2 + len(self.pswd)
            msg[9] |= 0xC0
        if self.keepalive:
            assert self.keepalive < 65536
            msg[10] |= self.keepalive >> 8
            msg[11] |= self.keepalive & 0x00FF
        if self.lw_topic:
            msg[1] += 2 + len(self.lw_topic) + 2 + len(self.lw_msg)
            msg[9] |= 0x4 | (self.lw_qos & 0x1) << 3 | (self.lw_qos & 0x2) << 3
            msg[9] |= self.lw_retain << 5
        self.sock.write(msg)
        #print(hex(len(msg)), hexlify(msg, ":"))
        self._send_str(self.client_id)
        if self.lw_topic:
            self._send_str(self.lw_topic)
            self._send_str(self.lw_msg)
        if self.user is not None:
            self._send_str(self.user)
            self._send_str(self.pswd)
        resp = self.sock.read(4)
        assert resp[0] == 0x20 and resp[1] == 0x02
        if resp[3] != 0:
            raise MQTTException(resp[3])
        return resp[2] & 1

    def disconnect(self):
        self.sock.write(b"\xe0\0")
        self.sock.close()

    def ping(self):
        self.sock.write(b"\xc0\0")

    def publish(self, topic, msg, retain=False, qos=0):
        pkt = bytearray(b"\x30\0\0\0")
        pkt[0] |= qos << 1 | retain
        sz = 2 + len(topic) + len(msg)
        if qos > 0:
            sz += 2
        assert sz < 2097152
        i = 1
        while sz > 0x7f:
            pkt[i] = (sz & 0x7f) | 0x80
            sz >>= 7
            i += 1
        pkt[i] = sz
        #print(hex(len(pkt)), hexlify(pkt, ":"))
        self.sock.write(pkt, i + 1)
        self._send_str(topic)
        if qos > 0:
            self.pid += 1
            pid = self.pid
            struct.pack_into("!H", pkt, 0, pid)
            self.sock.write(pkt, 2)
        self.sock.write(msg)
        if qos == 1:
            while 1:
                op = self.wait_msg()
                if op == 0x40:
                    sz = self.sock.read(1)
                    assert sz == b"\x02"
                    rcv_pid = self.sock.read(2)
                    rcv_pid = rcv_pid[0] << 8 | rcv_pid[1]
                    if pid == rcv_pid:
                        return
        elif qos == 2:
            assert 0

    def subscribe(self, topic, qos=0):
        assert self.cb is not None, "Subscribe callback is not set"
        pkt = bytearray(b"\x82\0\0\0")
        self.pid += 1
        struct.pack_into("!BH", pkt, 1, 2 + 2 + len(topic) + 1, self.pid)
        #print(hex(len(pkt)), hexlify(pkt, ":"))
        self.sock.write(pkt)
        self._send_str(topic)
        self.sock.write(qos.to_bytes(1))
        while 1:
            op = self.wait_msg()
            if op == 0x90:
                resp = self.sock.read(4)
                #print(resp)
                assert resp[1] == pkt[2] and resp[2] == pkt[3]
                if resp[3] == 0x80:
                    raise MQTTException(resp[3])
                return

    # Wait for a single incoming MQTT message and process it.
    # Subscribed messages are delivered to a callback previously
    # set by .set_callback() method. Other (internal) MQTT
    # messages processed internally.
    def wait_msg(self):
        res = self.sock.read(1)
        self.sock.setblocking(True)
        if res is None:
            return None
        if res == b"":
            raise OSError(-1)
        if res == b"\xd0":  # PINGRESP
            sz = self.sock.read(1)[0]
            assert sz == 0
            return None
        op = res[0]
        if op & 0xf0 != 0x30:
            return op
        sz = self._recv_len()
        topic_len = self.sock.read(2)
        topic_len = (topic_len[0] << 8) | topic_len[1]
        topic = self.sock.read(topic_len)
        sz -= topic_len + 2
        if op & 6:
            pid = self.sock.read(2)
            pid = pid[0] << 8 | pid[1]
            sz -= 2
        msg = self.sock.read(sz)
        self.cb(topic, msg)
        if op & 6 == 2:
            pkt = bytearray(b"\x40\x02\0\0")
            struct.pack_into("!H", pkt, 2, pid)
            self.sock.write(pkt)
        elif op & 6 == 4:
            assert 0

    # Checks whether a pending message from server is available.
    # If not, returns immediately with None. Otherwise, does
    # the same processing as wait_msg.
    def check_msg(self):
        self.sock.setblocking(False)
        return self.wait_msg()


WIFISSID='petitbonum.net'
WIFIPASS='LaraGut12 '

def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
 #   sta_if = WLAN(network.STA_IF)
    print('Scan Networks', sta_if.scan())
    while not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(WIFISSID, WIFIPASS)
        time.sleep(2)
       # while not sta_if.isconnected():
        #    pass
    print('network config:', sta_if.ifconfig())

#---End Wifi Config---

from machine import Pin

led = Pin(2, Pin.OUT, value=1)

#---MQTT Sending---

from time import sleep_ms
from ubinascii import hexlify
from machine import unique_id
import socket
#from umqtt import MQTTClient
#import umqtt

SERVER = "192.168.2.50"
CLIENT_ID = hexlify(unique_id())
TOPIC1 = b"/sensor1/tem"
TOPIC2 = b"/sensor1/hum"
TOPIC3 = b"/sensor1/led"

def envioMQTT(server=SERVER, topic="/foo", dato=None):
    try:
        c = MQTTClient(CLIENT_ID, server)
        c.connect()
        print('connect mqtt')
        c.publish(topic, dato)
        print('publish',dato)
        sleep_ms(200)
        c.disconnect()
        #led.value(1)
    except Exception as e:
        pass
        #led.value(0)

state = 0

def sub_cb(topic, msg):
    global state
    print((topic, msg))
    if msg == b"on":
        led.value(0)
        state = 1
    elif msg == b"off":
        led.value(1)
        state = 0

def recepcionMQTT(server=SERVER, topic=TOPIC3):
    c = MQTTClient(CLIENT_ID, server)
    # Subscribed messages will be delivered to this callback
    c.set_callback(sub_cb)
    c.connect()
    print('connect')
    c.subscribe(topic)
    print("Connected to %s, subscribed to %s topic" % (server, topic))
    try:
        c.wait_msg()
    finally:
        c.disconnect()

#---End MQTT Sending---


from machine import Pin
import onewire
import time, ds18x20
ow = onewire.OneWire(Pin(12))

def oneWire():
    ds = ds18x20.DS18X20(ow)
    roms = ds.scan()
    ds.convert_temp()
    x = 0
    for rom in roms:
        print(rom)
        x = ds.read_temp(rom)
        print('temperatur',x)

    return x

#import pyb
from machine import Timer
import time

##
# Ultrasonic library for MicroPython's pyboard.
# Compatible with HC-SR04 and SRF04.
#
# Copyright 2014 - Sergio Conde Gómez <skgsergio@gmail.com>
# Improved by Mithru Vigneshwara
# Modified by orsisam <orsi.amax@gmail.com> for
# compatibility with esp8266
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

#import pyb
import machine
import time

class Ultrasonic:
    def __init__(self, tPin, ePin):
        # WARNING: Don't use PA4-X5 or PA5-X6 as echo pin without a 1k resistor (Attention for PyBoard)
        self.triggerPin = tPin
        self.echoPin = ePin

        # Init trigger pin (out)
        self.trigger = machine.Pin(self.triggerPin)
        self.trigger.init(machine.Pin.OUT, pull=None, value=0)
        #self.trigger.PULL_DOWN()

        # Init echo pin (in)
        self.echo = machine.Pin(self.echoPin)
        self.echo.init(machine.Pin.IN, pull=None)

    def distance_in_inches(self):
        return (self.distance_in_cm() * 0.3937)

    def distance_in_cm(self):
        start = 0
        end = 0

        # Create a microseconds counter.
        #micros = pyb.Timer(2, prescaler=83, period=0x3fffffff)
        #micros.counter(0)

        # Send a 10us pulse.
        self.trigger.high()
        time.sleep_us(10)
        #pyb.udelay(10)
        self.trigger.low()

        # Wait 'till whe pulse starts.
        while self.echo.value() == 0:
            start = time.ticks_us()

        # Wait 'till the pulse is gone.
        while self.echo.value() == 1:
            end = time.ticks_us()

        # Deinit the microseconds counter
        # micros.deinit()

        # take time different between start and end pulse.
        differ = time.ticks_diff(start, end)

        # Calc the duration of the recieved pulse, divide the result by
        # 2 (round-trip) and divide it by 29 (the speed of sound is
        # 340 m/s and that is 29 us/cm).
        dist_in_cm = -1 * ((differ / 2) / 29)

        return dist_in_cm

#---Main Program---

#if __name__ == "__main__":
def main():
    print('start')
    do_connect()
    sleep_ms(10000)
    sensor1 = Ultrasonic(14, 13)
    p=port(2)
    led = machine.Pin(0, machine.Pin.OUT)
    led.value(0)
    while True:
  #  (tem,hum) = medirTemHum()
   # displaytem(tem,hum)
        tem = 'TEST1'
        hum = 'TEST2'
        temp = oneWire()
        dist = sensor1.distance_in_cm()
        print("Sensor1 (Metric System)", dist, "cm")

        envioMQTT(SERVER,TOPIC1,str(temp))
        envioMQTT(SERVER,TOPIC2,str(dist))
        #envioMQTT(SERVER,TOPIC2,())
        # recepcionMQTT()
        sleep_ms(5000)
        led.value(1)
        sleep_ms(5000)
        led.value(0)

#---END Main Program---
