import json
import time

from library.msgbus import msgbus


#from module.manager.vdm import vdm

class S0(msgbus):

    def __init__(self,hwHandle,cfg,logChannel):

        self._hwHandle = hwHandle
        self._cfg = cfg
        self._log = logChannel

        '''
        System parameter
        '''
        print('Startup',self._cfg)
        self._pin = int(self._cfg.get('GPIO',None))
        self._factor = int(self._cfg.get('FACTOR',1000))
        self._accuracyWatt = int(self._cfg.get('ACCURACY',360))
        self._attenuator = str(self._cfg.get('ATTENUATOR','UP'))
        self._trigger = str(self._cfg.get('TRIGGER','RISING'))
        self._debounce = int(self._cfg.get('DEBOUNCE',100))
        self._power = float(self._cfg.get('POWER',0))
        self._energy = float(self._cfg.get('ENERGY',0))

        '''
        Class variables
        '''
        self._powerData = []
        self._t_update = 0
        self._pulsCounter = 0


        '''
        Maintenance Counter
        '''

        log_msg = 'Start S0 Interface'
        self.msgbus_publish(self._log, '%s %s: %s %s %s' % ('DEBUG', self.whoami(), log_msg, self._pin, self._cfg))

        #self.config(cfg)
        self.setup()

    def __del__(self):
        #print('kill myself',self._VPM_ID)
        log_msg ='Kill myself'
        self.msgbus_publish(self._log, '%s %s: %s %s'%('CRITICAL',self.whoami(), log_msg, self._pin))

    def whoami(self):
        return type(self).__name__

    def setup(self):
   #     print('Config old stored values',self._power, self._energy)
        log_msg = 'Restore old Values'
        self.msgbus_publish(self._log, '%s %s: %s Pin: %s Power: %s Energy: %s' % ('DEBUG', self.whoami(), log_msg, self._pin, self._power, self._energy))

        self._powerData.append(self._power)
        self._t_update = time.time()

        self._accuracySec = 3600 * 1000 / self._factor / self._accuracyWatt
   #     print('accu',self._accuracySec)
        log_msg = 'Setup the timeout value for Zero detection'
        self.msgbus_publish(self._log, '%s %s: %s %s TimoutCounter %s' % ('DEBUG', self.whoami(), log_msg, self._pin, self._accuracySec))

        if not self._pin == None:
            self._hwHandle.ConfigIO(self._pin,'IN',self._attenuator)
            self._hwHandle.Edge(self._pin,self.callback,self._trigger,self._debounce)
        else:
           # print('PIN unknown')
            log_msg = 'Port Unknown'
            self.msgbus_publish(self._log, '%s %s: %s %s' % ('ERROR', self.whoami(), log_msg, self._pin))

        return True

    def callback(self,pin):
     #   print('CAllback',pin,self._pulsCounter)
        log_msg = 'Callback'
        self.msgbus_publish(self._log, '%s %s: %s %s' % ('DEBUG', self.whoami(), log_msg, self._pin))

        if self._pulsCounter > 1:

          #  print('Test',self._t_update,self._powerData)

            _timeCurrent = time.time()

            log_msg = 'Update calculation'
            self.msgbus_publish(self._log, '%s %s: %s %s %s %s' % ('DEBUG', self.whoami(), log_msg, self._pin, _timeCurrent, self._t_update))

            self._powerData.append(self.power(self._t_update,_timeCurrent))
            self._t_update = _timeCurrent

        else:
          #  print('First Puls now Start')
            log_msg = 'First Puls Received now Start counting'
            self.msgbus_publish(self._log, '%s %s: %s %s' % ('DEBUG', self.whoami(), log_msg, self._pin))

        self._pulsCounter = self._pulsCounter + 1

      #  print('callback',self._powerData)
        return True

    def get(self):
        _msg = {}
        _msg['POWER'] = self.getPower()
        _msg['ENERGY'] = self.energy()

        log_msg = 'GET method'
        self.msgbus_publish(self._log, '%s %s: %s %s %s' % ('DEBUG', self.whoami(), log_msg, self._pin, _msg))
     #   _msg['PULSE'] = self._totalPulsCount
      #  _msg['TIME'] = time.time() - self.startTime
        #print ('msg',_msg)
        #self._pulsCount = 0
        return _msg

    def getPower(self):

        _result = 0
        #print('getPower',self._t_update,self._powerData)

        if self._t_update < time.time() - self._accuracySec:
            _result = 0
           # print('Nothing')
        else:
            _result = self.average(self._powerData)
          #  print('Result',_result)
        del self._powerData[:]
        self._powerData.append(_result)

        return _result

    def average(self,datalist):
        _result = 0

        for item in datalist:
            _result = _result + item

        #print('Reslut',_result,len(datalist))
        _result = _result / len(datalist)
        return _result

    def power(self,t0,t2):
        t1 = t2 - t0
#        print (t1, self._factor)
        _watt = 3600 * 1000 / self._factor / t1
      #  print('Watt',_watt)
        log_msg = 'Calculate power'
        self.msgbus_publish(self._log, '%s %s: %s %s Result %s' % ('DEBUG', self.whoami(), log_msg, self._pin, _watt))
        return _watt

    def energy(self):
        energySum = float(self._pulsCounter / self._factor)
        energySum = energySum + self._energy

        log_msg = 'Calculate energy'
        self.msgbus_publish(self._log, '%s %s: %s %s Result %s' % ('DEBUG', self.whoami(), log_msg, self._pin, energySum))
        return energySum


