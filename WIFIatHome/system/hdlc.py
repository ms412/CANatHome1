
import array
import utime

class hdlc(object):
    def __init__(self,interface):

        self._rxTimeout = 5
        self._FRM_BYTE = 0x7D
        self._ESC_BYTE = 0x7E

        self._If = interface

    def txFrame(self):
        # print('StringRx')
        str = ''
        (state, data) = self.unframer()

        if 'COMPLET' in state:
            str = ''.join(chr(i) for i in data)
            print('String', str)

        return (state, str)

    def rxFrame(self, str):
        data = []
        for item in str:
            # print(item)
            data.append(ord(item))

        return (self.framer(data))

    def unframer(self):
        timeout = False
        timeoutValue = utime.time() + self._rxTimeout

        state = 'INIT'
        data = []

        if self._If.any():
            print('Data')
            while not(timeout):
                if self._If.any():
                    (id,type,fmi,canframe) = self._If.recv(0)
                    self._rxFrame += 1
                    for item in canframe:
                        self._rxByte += 1

#                    ''' Start Frame '''
                        if item == self._FRM_BYTE and state in 'INIT':
                            state = 'RUN'
                            print(state,item)
                          #  data.append(item)
#                    ''' End Frame '''
                        elif item == self._FRM_BYTE and state in 'RUN':
                            state = 'COMPLET'
                            print(state,item)
                          #  data.append(item)
                            return(state,data)
#                    ''' Stuffin Byte'''
                        elif item == self._ESC_BYTE and state in 'RUN':
                            state = 'STUFFING'
                            print(state,item)
  #                   ''' un-Stuffing'''
                        elif state in 'STUFFING':
                            data.append(item ^ 0x20)
                            state = 'RUN'
                            print(state,item)
                        else:
                            data.append(item)
   #          ''' Timeout '''
                elif utime.time()> timeoutValue:
                    state = 'TIMEOUT'
                    timeout = True
                    return(state,data)
        else:
            state = 'NODATA'
       #     print('NoData')

        return(state,data)


    def framer(self, data):
        size = len(data)
        #   print('Transmit',size,data)
        # self._arrayTx =[]
        state = 'INIT'
        buffer = array.array('B', [])
        buffer.append(self._FRM_BYTE)
        state = 'RUN'
        length = 0

        for item in data:
            # print('tt',size,item,len(self._arrayTx))
            size = size - 1
            #        print(len(buffer),item)

            if len(buffer) == 8:
                #        print('test', buffer)
                # self._canIf.send(buffer, self._address, timeout=500)
            #    self.canSend(buffer)
                if not self._If.send(buffer):
                    return False

                buffer = array.array('B', [])
                #     print('array',len(self._arrayTx))
                # print('state', self._state,self._arrayTx)

            # if 'INIT' in state:
            #    buffer.append(self._FRM_BYTE)
            #    buffer.append(item)
            #    state = 'RUN'
            if 'RUN' in state:
                if item in (self._FRM_BYTE, self._ESC_BYTE):
                    buffer.append(self._ESC_BYTE)
                    #           print(len(buffer),buffer)
                    if len(buffer) == 8:
                        # self._canIf.send(buffer, self._address, timeout=500)
                       # self.canSend(buffer)
                        if self._If.send(buffer):
                            buffer = array.array('B', [])
                        else:
                            return False

                    buffer.append(item ^ 0x20)
                    if len(buffer) == 8:
                        #self.canSend(buffer)
                        if self._If.send(buffer):
                            buffer = array.array('B', [])
                        else:
                            return False

                else:
                    print(item)
                    buffer.append(item)
                    #  elif size <= 0:
                    #     print('end')

        buffer.append(self._FRM_BYTE)
       # self.canSend(buffer)
        if not self._If.send(buffer):
            return False
        #  self._canIf.send(buffer, self._address, timeout=500)

        return size
