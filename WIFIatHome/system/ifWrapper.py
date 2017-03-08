import ujson

from system.canIf import canIf
from system.hdlc import hdlc


class ifWrapper(object):
    def __init__(self,bitrate,filter,callback):
        self._commIf = canIf()
        self._commIf.bitrate(bitrate)
        self._commIf.filter(filter)
        self._hdlc = hdlc(self._commIf)
        self._callback = callback
        print('start can if')

    def run(self):
        while True:
        #    (state, data) = self._commIf.rxString()
            (state, data) = self._hdlc.txFrame()
            if 'COMPLET' in state:
                self._callback(ujson.loads(data))
                #				msg = ujson.loads(data)
                #                object = msg.get('OBJECT')
                #                method = msg.get('METHOD')
                #                value = msg.get('VALUE')
         #       print('DATA', state, data)

            yield

    def sink(self, msg):
       # self._commIf.txString(ujson.dumps(msg))
        self._hdlc.rxFrame(ujson.dumps(msg))