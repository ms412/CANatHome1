#!/usr/bin/env python3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


__app__ = "S02mqtt Adapter"
__VERSION__ = "0.81"
__DATE__ = "23.04.2016"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2016 Markus Schiesser"
__license__ = 'GPL v3'


import sys
import time
import json

from configobj import ConfigObj
from library.mqttclient import mqttpush
from library.logging import log_adapter
from library.msgbus import msgbus
from library.msgAdapter import msgAdapter

from library.gpio import gpio

class manager(msgbus):

    def __init__(self,cfg_file='S02mqtt.conf'):

        self._cfg_file = cfg_file

        self._cfg_broker = None
        self._cfg_logging = None
        self._cfg_gpio = None

    def whoami(self):
        return type(self).__name__

    def read_config(self):

        _cfg = ConfigObj(self._cfg_file)
     #   print('logg',_cfg)

        self._cfg_broker = _cfg.get('BROKER',None)
        self._cfg_logging = _cfg.get('LOGGING',None)
        self._cfg_gpio = _cfg.get('GPIO',None)
        self._cfg_msgAdapter = _cfg.get('BROKER',None)
        return True

    def start_logging(self):
        self._log_thread = log_adapter(self._cfg_logging)
        self._log_thread.start()
        return True

    def start_mqttbroker(self):
        self._mqttbroker = mqttpush(self._cfg_broker)
        self.msgbus_subscribe('MQTT_SNK',self._mqttbroker.push)
       # self._mqttbroker = mqttbroker(self._cfg_broker,'MQTT_SNK','MQTT_SRC','LOG')
       # self._mqttbroker.start()
        return True

    def start_gpio(self):
      #  self.msgbus_subscribe('GPIO_SRC',self.gpio2mqtt)
        self._gpio = gpio(self._cfg_gpio,'GPIO_SNK','GPIO_SRC','LOG')
        self._gpio.start()
        return True

    def start_msgAdapter(self):
        self._msgAdapter = msgAdapter(self._cfg_msgAdapter,'GPIO_SNK','GPIO_SRC','MQTT_SNK','MQTT_SRC','LOG')
       # self.msgbus_subscribe('GPIO_SRC', self._msgAdapter.dataSrc)
        #self._msgAdapter.start()
        return True


    def run(self):
        """
        Entry point, initiates components and loops forever...
        """
        self.read_config()
        self.start_logging()
        time.sleep(2)

        log_msg = 'Startup S02mqtt Adapter'
        self.msgbus_publish('LOG','%s %s: %s %s %s %s' % ('INFO', self.whoami(), log_msg, __app__, __VERSION__, __DATE__))
        self.start_mqttbroker()
        self.start_msgAdapter()
        self.start_gpio()

        while(True):
            if not self._gpio.isAlive():
                log_msg = 'GPIO Thread died'
                self.msgbus_publish('LOG', '%s %s: %s' % ('CRITICAL', self.whoami(), log_msg))
                self._gpio.__del__()
                self.start_gpio()

            else:
                time.sleep(10)

      #  self.start_socketcan()
       # self.start_adapter()




if __name__ == "__main__":

    print ('main')
    if len(sys.argv) == 2:
        configfile = sys.argv[1]
    else:
        configfile = 'S02mqtt.conf'

   # print('Configfile',configfile)
    mgr_handle = manager(configfile)
    mgr_handle.run()