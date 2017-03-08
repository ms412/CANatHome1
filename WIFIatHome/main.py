# main.py -- put your code here!

from module.gpio import input, output
from module.system import heardbeat
from module.system import watchdog
from module.tempfile import tempfile
from system.ifWrapper import ifWrapper
from system.objRegistry import objRegistry
from system.usched import Sched

from system.msgAdapter import msgAdapter


class kill(object):
    def stop(self,fTim, objSch):                                     # Stop the scheduler after fTim seconds
        yield fTim
        print('Stopping')
        objSch.stop()

class manager(object):

    def __init__(self,cfgFile='config.cfg'):

        self._cfgFile = cfgFile

        self._config = None
        print(self._cfgFile)
        

        self._cfgCommIf = None
        self._cfgGpio = None
		
        self._commIf = None
        self._objRegister = None    #object register
        self._threadObj = None       #scheduler register
        self._msgAdapter = None     #message adapter
        self._system = None

    def readConfig(self):
        temp = tempfile(self._cfgFile)
        self._config = temp.openfile()
        
        print('Read Configuration',self._config.get('COMMUNICATION',None))
        self._cfgCommIf = self._config.get('COMMUNICATION',None)
        self._cfgGpio = self._config.get('GPIO',None)
        self._cfgSystem = self._config.get('SYSTEM',None)

    def msgAdapter(self):
        print('START Message Adapter')
        self._msgAdapter = msgAdapter(self._objRegister,self._commIf)

    def scheduler(self):
        print('Create Scheduler')
        self._threadObj = Sched()

    def objRegister(self):
        print('Create object Registry')
        self._objRegister = objRegistry()
     #   lamp001 = lamp()
   #     ping001 = ping()
    #    systemTime001 = systemTime()
     #   self._objRegister.register('lamp001',lamp001)
      #  self._objRegister.register('PING',ping001)
      #  self._objRegister.register('TIME',systemTime001)
		
    def commIf(self):
        print('START Comm interface',self._cfgCommIf)
        commIf = self._cfgCommIf.get('COM')
        if 'WIFI' in commIf:
            print('WIFI')
        else:
            print('CAN')
            bitrate = self._cfgCommIf.get('BITRATE',125)
            filter = self._cfgCommIf.get('CAN-ID',255)
            self._commIf = ifWrapper(bitrate,filter,self._msgAdapter.commIf)
            self._msgAdapter.setMsgSink(self._commIf.sink)
            self._threadObj.add_thread(self._commIf.run())

    def system(self):
        print('start System',self._cfgSystem)
        heardbeatConfig = self._cfgSystem.get('HEARDBEAT',None)
        heardbeatConfig['VERSION']=self._cfgSystem.get('VERSION',None)
        heardbeatConfig['SYSTEM-ID']=self._cfgSystem.get('SYSTEM-ID',None)
        heardbeatConfig['CAN-ID']=self._cfgCommIf.get('CAN-ID',0)
        heardbeatObj = heardbeat(heardbeatConfig,self._msgAdapter.sink)
        self._threadObj.add_thread(heardbeatObj.run())

    def watchdog(self):
        #watchdogConfig = int(self._cfgSystem.get('WATCHDOG',2000))
        #print('watchdog',watchdogConfig)

        # in msec, default 20 sec
        watchdogObj = watchdog(20000)
        self._threadObj.add_thread(watchdogObj.run())

		
    def gpioConfig(self):
        print('START GPIO',self._cfgGpio)
        for key, value in self._cfgGpio.items():
            if "OUTPUT" in key:
           #     print('fff',value)
                for portName, portConfig in value.items():
              #      print('xxx',portName,portConfig)
                    portObj = output(portName,portConfig,self._msgAdapter.sink)
                    self._objRegister.register(portName,portObj)
                    self._threadObj.add_thread(portObj.run())
            elif "INPUT" in key:
                for portName, portConfig in value.items():
               #     print('xxx',portName,portConfig)
                    portObj = input(portName,portConfig,self._msgAdapter.sink)
                    self._objRegister.register(portName,portObj)
                    self._threadObj.add_thread(portObj.run())
            else:
                print('unknown config type')



    def startSystem(self):
        duration = 50
        self.readConfig()
        self.scheduler()

        self.objRegister()
        self.msgAdapter()

        self.commIf()

        self.system()
        self.watchdog()
        self.gpioConfig()


    #    kill1 = kill()

      #  if duration:
       #     self._threadObj.add_thread(kill1.stop(duration, self._threadObj))  # Kill after a period

        self._threadObj.run()




if __name__ == '__main__':
	
    mgr = manager('config.cfg')
    mgr.startSystem()