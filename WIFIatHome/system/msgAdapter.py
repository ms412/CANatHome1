class msgAdapter(object):
    def __init__(self,objRegister,commIf):
        self._objRegister = objRegister
        self._commIf = commIf
    #    print('objregisert',objRegister)
        self._msgSink = None

    def setMsgSink(self,sink):
        self._msgSink = sink
        print('msgAdapter sink', self._msgSink)

    def sink(self,msg):
        print('Message arrived in sink',msg)
        print(msg.get('CAN-ID',None))
        if msg.get('CAN-ID',None) is None:
            print('local message')
            self.commIf(msg)
        else:
            self._msgSink(msg)

        return True

    def commIf(self,msg):
        print('can message arrive',msg)
        object = msg.get('OBJECT',None)
        method = msg.get('METHOD',None)
        value = msg.get('VALUE',None)
        print('objregisert', self._objRegister,object,method)
        obj = self._objRegister.getObject(object)
        if obj is not None:
            methodToCall = getattr(obj, method)
            methodToCall(value)
        return True
