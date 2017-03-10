import json
import time

from library.msgbus import msgbus


#from module.manager.vdm import vdm

class S0(msgbus):

    def __init__(self,hwHandle,pin,cfg,logChannel):


       # self._VPM_ID = int(cfg.get('HW-IF'))
        self._VPM_ID = pin
        self._hwHandle = hwHandle
        self._cfg = cfg
        self._log = logChannel

        '''
        System parameter
        '''
        self._mode = 'S0'
        self._hwid = int(cfg.get('HW-IF'))

        '''
        Class variables
        '''
        self._pin_save = 'Unknown'
        self._tempBuffer = []
        self._T0 = time.time()

        self._pulsCount = 0

        self._totalPulsCount = cfg.get('PULSE',0)

        self._saveEnergy = cfg.get('ENERGY',0)

       # self._update = False

        '''
        Maintenance Counter
        '''
        self._counter = 0

        log_msg = 'Start S0 Interface'
        self.msgbus_publish(self._log, '%s %s: %s %s %s' % ('DEBUG', self.whoami(), log_msg, self._VPM_ID, self._cfg))

        self.config(cfg)

    def __del__(self):
        #print('kill myself',self._VPM_ID)
        logmsg ='Kill myself'
        self.msgbus_publish('LOG','%s VPM Mode: %s ID: %s Message: %s'%('CRITICAL', self._mode, self._VPM_ID, logmsg))

    def whoami(self):
        return type(self).__name__

    def config(self,msg):
        '''
        :param msg: contains configuration as a tree object
        :return:
        '''


       # print('Config interface S0', self._VPM_ID)

        self._factor = int(self._cfg.get('FACTOR',0))
        #self._hwid = int(cfg.getNode('HWID',None))

        if self._hwid is None:
            logmsg = 'HWID is missing in config'
            self.msgbus_publish(self._log,'%s %s: %s'%('CRITICAL', self._mode, self._VPM_ID, logmsg))
        #   print('S0 VPM::ERROR no HWID in config')
        else:
          #  print('S0 VPM:', self._hwid)
            self._hwHandle.ConfigIO(self._hwid,'IN')

            '''
            Define class variables
            '''
            self._SavePinState = 0

            self._T0 = time.time()
            self._T1 = 0.0
            self._T2 = 0.0
         #   self._T3 = time.time()

            self._baseState = 0

            self._ResultAvailable = False

            self._watt = 0.0
            self._energySum = 0.0
            self._energyDelta = 0.0
            self._pulsCount = 0

            self.waitNextUpEvent = False
            self.startTime = self._T0
        return True

    def run(self):
        '''
        run is getting called on a regular base from VDM, frequency of calls defined by update value in VDM configuration section
        '''

       # print('update')
  #      print('run',self._hwHandle.ReadPin(self._hwid),self._hwid)
    #    print('stat',self._SavePinState,self._hwHandle.ReadPin(self._hwid))
        _currentPinState = self._hwHandle.ReadPin(self._hwid)
        #print('PinState',_currentPinState)

        # pulse down event
        if self._SavePinState == 1 and _currentPinState == 0:
            startTime = time.time()
            self.waitNextUpEvent = True
           # print('pulse down event',self._VPM_ID)
            log_msg = 'Event Puls Down'
            self.msgbus_publish(self._log,'%s %s: %s %s' % ('DEBUG', self.whoami(), log_msg, self._VPM_ID))


        # pulse up event
        elif self._SavePinState == 0 and _currentPinState == 1:

           # print ("State2")
           # print ("SavePinState", self._SavePinState)
           # print ("PinState", self._hwHandle.ReadPin(self._hwid))
          #  print('pulse up event',self._VPM_ID)
            log_msg = 'Event Puls Up'
            self.msgbus_publish(self._log, '%s %s: %s %s' % ('DEBUG', self.whoami(), log_msg, self._VPM_ID))
            if self.waitNextUpEvent == True:
                self.waitNextUpEvent = False
                self._pulsCount = self._pulsCount + 1
                self._totalPulsCount = self._totalPulsCount + 1
                self._tempBuffer.append(time.time() -  startTime)
             #   print('Counter increase',self._VPM_ID,self._pulsCount)
                log_msg = 'Increase Counter'
                self.msgbus_publish(self._log, '%s %s: %s %s %s' % ('DEBUG', self.whoami(), log_msg, self._VPM_ID, self._pulsCount))

        self._SavePinState = _currentPinState

      #  return update
       # self._counter = self._counter +1


        return True

    def get(self):
        _msg = {}
        _msg['POWER'] = self._power1()
        _msg['ENERGY'] = self._energy2()
     #   _msg['PULSE'] = self._totalPulsCount
      #  _msg['TIME'] = time.time() - self.startTime
        self._pulsCount = 0
        return _msg

    def _power(self):
      #  self._watt = self._pulsCount/self._factor * 3600 / time.time()
        if self._pulsCount > 0:

            self._T2 = time.time()- self._T0
            self._T0 = time.time()
       # print('Time T2',self._T2,self._pulsCount)
            self._watt = self._pulsCount/self._T2 * 3600

            log_msg = 'Counter Power'
            self.msgbus_publish(self._log, '%s %s: %s %s %s %s' % ('DEBUG', self.whoami(), log_msg, self._VPM_ID, self._pulsCount, self._T2))
        else:
            log_msg = 'Counter Power no update'
            self.msgbus_publish(self._log, '%s %s: %s %s %s %s' % ('DEBUG', self.whoami(), log_msg, self._VPM_ID, self._pulsCount, time.time()- self._T0))
            self._watt = 0

        return self._watt

    def _power1(self):
        sumTime = 0
        print('Test001',len(self._tempBuffer))
        if len(self._tempBuffer) > 0:
            for item in self._tempBuffer:
                sumTime = sumTime + item
                watt = len(self._tempBuffer)/sumTime*3600
        else:
            watt = 0

        return watt


    def _energy(self):
        energyCurr = float(self._pulsCount / self._factor)
        #print('Current Engergy',energyCurr)
        return energyCurr

    def _energy1(self):
       # print('Energy1',self._totalPulsCount,self._saveEnergy,time.time() - self.startTime)
      #  energySum = float(self._pulsCount*self._factor /3600/(time.time() - self.startTime))
        energySum = float(self._totalPulsCount / (time.time() - self.startTime) * 1 / self._factor )
        energySum = energySum + self._saveEnergy
        return energySum

    def _energy2(self):
        energySum = float(self._totalPulsCount/self._factor)
        energySum = energySum + self._saveEnergy
        return energySum

    def _energy24h(self):

        return True

    def _energyMonth(self):

        return True

    def _energyYear(self):

        return True
