
from queue import Queue
import time
#from datetime import datetime, timezone
from threading import Thread, Lock

from library.msgbus import msgbus
'''
INFO -> all information path no filter

DEBUG
WARNING
ERROR
CRITICAL
'''

class log_adapter(Thread, msgbus):
    '''
    classdocs
    '''

    def __init__(self,config):
        Thread.__init__(self)
      #  print('init logging',config)

        self._logLevelValues = {'DEBUG':0, 'WARNING': 1, 'ERROR': 2, 'CRITICAL':3, 'INFO':9}

        self._logFile = config.get('LOGFILE','S02mqtt.log')
        self._loglevel = config.get('LOGLEVEL','CRITICAL')
       # print('loglevel',self._loglevel)

        self._logFilterLevel = self._logLevelValues.get(self._loglevel,3)

        #print('LogFilterLevel', self._logFilterLevel)

        self.log_queue = Queue()

        self._logFileHandle = None

    def run(self):
        #print('run logging adapter')

        self.setup()


        threadRun = True

        while threadRun:
            time.sleep(5)
            self.openfile()
            while not self.log_queue.empty():
                    # self.on_log(self.log_queue.get())
                self.write(self.log_queue.get())

            self.closefile()

        return True

    def setup(self):
        self.msgbus_subscribe('LOG', self._on_log)
        return True

    def _on_log(self, log_msg):
      #  print('LOG:',log_msg)
       # self.log_queue.put(log_msg)
        self.filter(log_msg)
        return True

    def filter(self,log_msg):
        _list_log_msg =log_msg.split()
        _msg_level = self._logLevelValues.get(_list_log_msg[0],9)

        if _msg_level >= self._logFilterLevel:
            self.log_queue.put(log_msg)

        return True

    def openfile(self):
      #  print('LOG: Openlogfile', self._logFileName)
        self._logFileHandle = open(self._logFile, "a")
        return True

    def closefile(self):
     #   print('LOG: Closelogfile', self._logFileHandle)
        self._logFileHandle.closed
        return True

    def write(self, logdata):
      #  print('LOG timestamp:',self.timestamp())
        self._logFileHandle.write(str(self.timestamp()) + '\t' + logdata + '\n')
       # self._logFileHandle.write(logstring)
        return True

    def timestamp(self):
      #  print( time.strftime("%Y-%m-%d %H:%M:%S"))
        return time.strftime("%Y-%m-%d %H:%M:%S")
        #print (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
     #   print('Test ', datetime.now(timezone.utc).astimezone().isoformat())
        #return datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') #.format
