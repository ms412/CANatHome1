__author__ = 'oper'


import time
import os
#import library.libpaho as mqtt
import paho.mqtt.client as mqtt

from queue import Queue
from library.msgbus import msgbus

class mqttpush(object):

    def __init__(self,config):
        '''
        setup mqtt broker
        config = dictionary with configuration
        '''

        self._config = config

        '''
        create mqtt session
        '''
        #self.create()
        self._mqttc = mqtt.Client(str(os.getpid()),clean_session=True)

        self._host = str(self._config.get('HOST','localhost'))
        self._port = int(self._config.get('PORT',1883))
        self._user = str(self._config.get('USER',None))
        self._password = str(self._config.get('PASSWD',None))
        self._publish = str(self._config.get('PUBLISH','/PUBLISH'))

    def push(self,channel,msg):
        self._mqttc.connect(self._host)
        self._mqttc.publish(channel,msg)
      #  print('cc',self._publish,msg)
        self._mqttc.loop(2)
        self._mqttc.disconnect()
        return True


class mqttbroker(msgbus):

    def __init__(self,config,msgSink,msgSource,logChannel):
        '''
        setup mqtt broker
        config = dictionary with configuration
        '''

        self._config = config
        self._msgSink = msgSink
        self._msgSource = msgSource
        self._log = logChannel

        self._published = False

        '''
        broker object
        '''
        self._mqtt = ''

        '''
        Transmit and Receive Queues objects
        '''
        self._rxQueue = Queue()

       # print('MQTT: Init Mqtt object Startup', self)
        #msg = 'Create Object'
       # self.msgbus_publish(self._log,'%s Libmqtt: %s '%('DEBUG',msg))
        '''
        create mqtt session
        '''
        #self.create()
        self._mqttc = mqtt.Client(str(os.getpid()),clean_session=True)

    def __del__(self):
        msg = 'Delete object'
        self.msgbus_publish(self._log,'%s %s: %s '%('CRITICAL',self.whoami(),msg))
      #  print("Delete libmqttbroker")
        self._mqttc.disconnect()

    def whoami(self):
        return type(self).__name__

    def start(self):
        '''
        start broker
        '''
        msg = 'Start MQTT Broker Interface with configuration'
        self.msgbus_publish(self._log,'%s %s: %s %s'%('INFO',self.whoami(),msg, self._config))

        self.setup()
        self.connect(self._host,self._port)
        self.subscribe(self._subscribe)

        self.msgbus_subscribe(self._msgSink,self.send)

        return True

    def setup(self):
        '''
        broker Configuration
        '''
        self._host = str(self._config.get('HOST','localhost'))
        self._port = int(self._config.get('PORT',1883))
        self._user = str(self._config.get('USER',None))
        self._password = str(self._config.get('PASSWD',None))
        self._subscribe = str(self._config.get('SUBSCRIBE',None))
        self._subscribe +='#'
        self._publish = str(self._config.get('PUBLISH','/PUBLISH'))

        '''
        setup callbacks
        '''
        self._mqttc.on_message = self.on_message
        self._mqttc.on_connect = self.on_connect
        self._mqttc.on_publish = self.on_publish
        self._mqttc.on_subscribe = self.on_subscribe
        self._mqttc.on_disconnect = self.on_disconnect
        self._mqttc.on_log = self.on_log
        #self._mqttc.on_log = self.on_log

        return True

    def send(self,message):
      #  msg = 'Messages transmit'
       # self.msgbus_publish(self._log, '%s %s: %s' % ('DEBUG', self.whoami(), msg))
        if self._published:
            time.sleep(0.1)
            if self._published:
                self.reinitialise()

        self.publish(message)
        return True

    def receive(self):
        if not self._rxQueue.empty():
            msg = self._rxQueue.get()
         #   message = msg.get('MESSAGE',None)
          #  channel = msg.get('CHANNEL',None)
        else:
            msg = None
           # channel = None

        return msg


    def on_connect(self, client, userdata, flags, rc):
       # print('MQTT:: connect to host:', self._host,client,userdata,flags,str(rc))
        msg = 'Connected to MQTT broker'
        self.msgbus_publish(self._log,'%s %s: %s'%('DEBUG',self.whoami(),msg))
        self._connectState = True
        return True

    def on_disconnect(self, client, userdata, rc):
        msg = 'Disconnect from MQTT broker'
        self.msgbus_publish(self._log, '%s %s: %s' % ('DEBUG', self.whoami(), msg))
        return True

    def on_message(self, client, userdata, msg):
        message ={}
        message.update({'CHANNEL':msg.topic})
        message.update({'PAYLOAD':msg.payload})

        log_msg = 'Message received'
        self.msgbus_publish(self._log, '%s %s: %s %s' % ('DEBUG', self.whoami(), msg, message))
        self.msgbus_publish(self._msgSource,message)
        return True

    def on_publish(self, client, userdata, mid):
        msg = 'Message published'
        self.msgbus_publish(self._log, '%s %s: %s' % ('DEBUG', self.whoami(), msg))
        self._published = False
        return True

    def on_subscribe(self, client, userdata, mid, granted_qos):
        msg = 'Subscribed'
        self.msgbus_publish(self._log, '%s %s: %s' % ('DEBUG', self.whoami(), msg))
        return True

    def on_unsubscribe(self, client, userdata, mid):
        msg = 'Unsubscribe from Channel'
        self.msgbus_publish(self._log, '%s %s: %s' % ('DEBUG', self.whoami(), msg))
        return True

    def on_log(self,client, userdata, level, buf):
        msg = 'MQTT log information'
        self.msgbus_publish(self._log, '%s %s: %s; %s; %s; %s; %s' % ('CRITICAL', self.whoami(), msg, client, userdata, level, buf))
        return True

    def reinitialise(self):
        msg = 'Reinitialise Connection to MQTT Broker'
        self.msgbus_publish(self._log, '%s %s: %s' % ('DEBUG', self.whoami(), msg))
        self._mqttc.reinitialise(str(os.getpid()), clean_session=True)
        return True

    def connect(self,host,port):
        msg = 'Connect to Broker'
        self.msgbus_publish(self._log, '%s %s: %s: %s : %s' % ('DEBUG', self.whoami(), msg, host, port))
        self._mqttc.connect(host, port,60)
        self._mqttc.loop_start()
        return True

    def disconnect(self):
        self._mqttc.disconnect()
        return True

    def subscribe(self,channel = None):
        msg = 'Subscribed to Channel'
        self.msgbus_publish(self._log, '%s %s: %s: %s' % ('DEBUG', self.whoami(), msg, channel))
        self._mqttc.subscribe(channel,0)
        return True

    def unsubscribe(self,channel):
        msg = 'Unsubscribed from Channel'
        self.msgbus_publish(self._log, '%s %s: %s: %s' % ('DEBUG', self.whoami(), msg, channel))
        self._mqttc.unsubscribe(self._subscribe)
        return True

    def publish(self,message):
        msg = 'Publish Message'
        self.msgbus_publish(self._log, '%s %s: %s Channel: %s Message: %s' % ('DEBUG', self.whoami(), msg, message.get('CHANNEL'), message.get('PAYLOAD')))
        self._mqttc.publish(message.get('CHANNEL'), message.get('PAYLOAD'), 0)
        self._published = True
        return True

if __name__ == "__main__":

    config1 = {'HOST':'192.168.1.107','PUBLISH':'/TEST','SUBSCRIBE':'/TEST/','CONFIG':'/TEST2/'}
    config2 = {'HOST':'localhost','PUBLISH':'/TEST','SUBSCRIBE':['/TEST1/#','/TEST3','/TEST4']}
    msg = {'CHANNEL':'/TEST/CONFIG','MESSAGE':'{ioioookko}'}
    broker = mqttbroker(config1)
  #  broker = setup(config)
 #   broker.start()

#    broker.connect()
 #   broker.subscribe()
    time.sleep(10)
    broker.restart(config1)
 #   time.sleep(10)

    while True:
        time.sleep(1)
        #broker.publish(msg)
   # time.sleep(2)
