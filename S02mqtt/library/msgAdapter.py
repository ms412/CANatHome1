
import json
#from threading import Thread, Lock
from library.msgbus import msgbus
import paho.mqtt.publish as publish
from library.mqttclient import mqttpush


class msgAdapter(msgbus):
    '''
    classdocs
    '''

    def __init__(self,config,dataSnk,dataSrc,brokerSnk,brokerSrc,logChannel):
    #    Thread.__init__(self)
     #   print('init logging',config)

        self._cfg = config
        self._dataSnk = dataSnk
        self._dataSrc = dataSrc
        self._brokerSnk = brokerSnk
        self._brokerSrc = brokerSrc
        self._log = logChannel

        self._msgSnk = self._cfg.get('PUBLISH',None)
        self._msgSrc = self._cfg.get('SUBSCRIBE',None)
        self._mqttHost = self._cfg.get('HOST',None)

        self.setup()

    def __del__(self):
        log_msg = 'Delete myself'
        self.msgbus_publish(self._log, '%s %s: %s ' % ('DEBUG', self.whoami(), log_msg))

    def whoami(self):
        return type(self).__name__

    def setup(self):
        log_msg ='startup with config'
        self.msgbus_publish(self._log, '%s %s: %s: %s' % ('DEBUG',self.whoami(), log_msg, self._cfg))

        if self._msgSnk == None:
            log_msg = 'mandatory Parameter PUBLISH not in configfile'
            self.msgbus_publish(self._log, '%s %s: %s ' % ('CRITICAL', self.whoami(), log_msg))
            return False

     #   self.msgbus_subscribe('GPIO_SRC', self.dataSrc)
        self.msgbus_subscribe('GPIO_SRC', self.transmit)


        return True

    def dataSrc(self,msg):
       # print('zzzzzzzzz',msg)
        message = {}

        for key,value in msg.items():
            message['CHANNEL'] = self._msgSnk + key
            message['PAYLOAD'] = json.dumps(value)

        #    print('uuuuuuuuuuu',message)

            self.msgbus_publish(self._brokerSnk, message)

            publish.single("/OPENHAB", json.dumps(value), hostname='192.168.2.50')

        return True

    def transmit(self,msg):
       # print('transmit',msg)

        for key, value in msg.items():
            channel = self._msgSnk + key
            message = json.dumps(value)

        #    publish.single(channel, message, hostname=self._mqttHost)
            self.msgbus_publish('MQTT_SNK',channel,message)
            log_msg = 'Publish message'
            self.msgbus_publish(self._log, '%s %s: %s Channel: %s Message: %s' % ('DEBUG', self.whoami(), log_msg, channel, message))

        return True
