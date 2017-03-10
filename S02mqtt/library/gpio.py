
from threading import Thread
from threading import Event
from queue import Queue
import time

from library.msgbus import msgbus


'''
import device interface drivers
'''
from library.raspberry import raspberry
#from library.dummy import dummy
#from module.devices.mcp23017 import MCP23017

'''
import port manager
'''
from library.S0 import S0
from library.tempfile import tempfile

class gpio(Thread,msgbus):

    def __init__(self,config,sink,source,logChannel):
        Thread.__init__(self)


        self._cfg = config
        self._msgSink = sink
        self._msgSource = source
        self._log = logChannel
        self._tmpfilename = self._cfg.get('TEMPFILE','S02mqtt.temp')
        #del self._cfg['TEMPFILE']

        '''
        Hardware handel stores the handle to the hardware
        only once available per VDM instance
        '''
        self._hwHandle = None
        self._devHandle = {}

        self._counter = 0
        self._power = 0
        self._energy = 0
        self._result = {}

        self._threadRun = True

        self.msg = {}

        log_msg = 'Startup GPIO Adapter with config'
        self.msgbus_publish(self._log,'%s %s: %s %s' % ('INFO', self.whoami(), log_msg, self._cfg))

        self.setup()

    def __del__(self):
        '''
        stop all concerning VPM objects before destroying myself
        '''

        for key, value in self._VPMobj:
            del value

        self.msgbus_publish(self._log,'%s GPIO Module Destroying myself: %s '%('DEBUG', self._DevName))

    def whoami(self):
        return type(self).__name__

    def setup(self):
        self._tempFile = tempfile(self._tmpfilename, self._log)
        tmpdata = self._tempFile.openfile()

        if tmpdata == None:
          #  print('file does not exist')
            log_msg = 'Tempfile does not exist'
            self.msgbus_publish(self._log,'%s %s: %s %s' % ('DEBUG', self.whoami(), log_msg, self._tmpfilename))
        else:
            #print('Data',tmpdata)
            log_msg = 'Tempfile exit read old values'
            self.msgbus_publish(self._log, '%s %s: %s %s' % ('INFO', self.whoami(), log_msg, tmpdata))


     #   print('Config',self._cfg)
        #self._hwHandle = dummy()
        self._hwHandle = raspberry(self._log)

        for _pin, _cfg in self._cfg.items():
            print(_pin, _cfg)
            if isinstance(_cfg, dict):
                if tmpdata != None:
                    _tmp = tmpdata.get(_pin,None)
                    #print('Temp',_tmp,_pin,tmpdata.get('ENERGY',0))
                    if None == _tmp:
                        _cfg['ENERGY'] = 0
                        _cfg['POWER'] = 0
                    else:
                        _cfg['ENERGY'] = _tmp.get('ENERGY',0)
                        _cfg['POWER'] = _tmp.get('POWER',0)
           #        _cfg['TIME'] = _tmp.get('TIME',0)

                #self._devHandle[_pin] = S0(self._hwHandle, _pin, _cfg, self._log)
                self._devHandle[_pin] = S0(self._hwHandle, _cfg, self._log)

    def run(self):

      #  self.msgbus_publish(self._log,'%s VDM Virtual Device Manager %s Startup'%('INFO', self._DevName))
       # threadRun = True


        _timeT0 = time.time()
        _timeDelta = 60
        _timeT1 = _timeT0 + _timeDelta


        while self._threadRun:
            time.sleep(0.3)
           # for key,value in self._devHandle.items():
          #      print('.',key,value)
                #value.run()

          #  print('Test',_timeT1,time.time())
            if time.time() > _timeT1:
              #  print('Send update')
                log_msg = 'Timer expired get update'
                self.msgbus_publish(self._log, '%s %s: %s ' % ('DEBUG', self.whoami(), log_msg))

                for key,value in self._devHandle.items():
          #         print('.',key,value)
                    self.msg[key]=value.get()
                    self._tempFile.writefile(self.msg)

              #  print('power',self.msg)
                log_msg = 'Send Update'
                self.msgbus_publish(self._log, '%s %s: %s %s' % ('DEBUG', self.whoami(), log_msg, self.msg))
                self.msgbus_publish(self._msgSource,self.msg)

                _timeT1 = time.time() + _timeDelta