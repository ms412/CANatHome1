import json
from library.msgbus import msgbus

class tempfile(msgbus):

    def __init__(self,filename,logChannel):

        self._filename = filename
        self._log = logChannel

        msg = 'Create object with config'
        self.msgbus_publish(self._log, '%s %s: %s: %s ' % ('DEBUG', self.whoami(), msg,self._filename))

    def __del__(self):
        msg = 'Delete object'
        self.msgbus_publish(self._log,'%s %s: %s '%('CRITICAL',self.whoami(),msg))

    def whoami(self):
        return type(self).__name__

    def openfile(self):

        try:
            with open(self._filename)as fh:
                data = json.load(fh)
            #    print('test',data)
                fh.close()
                msg = 'Data File exist startup with historical data'
                self.msgbus_publish(self._log,'%s %s: %s: %s '%('DEBUG',self.whoami(),msg,data))
        except IOError:
       #     print ('File doese not exist')
            msg = 'Data File does not exist startup without historical data'
            self.msgbus_publish(self._log, '%s %s: %s ' % ('INFO', self.whoami(), msg))
            data = None

        return data


    def writefile(self,data):

            with open(self._filename,'w')as fh:
                json.dump(data,fh,indent =4)
                msg = 'Save Data to file'
                self.msgbus_publish(self._log,'%s %s: %s: %s '%('DEBUG',self.whoami(),msg,data))
