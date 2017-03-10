
import random

class dummy(object):

    def __init__(self):

        print('Dummy')

    def Reset (self):
        return True


    def setup(self, mode, pin):

        return True


    def ConfigIO(self,ioPin,iodir):

        return True


    def ConfigPWM(self,ioPin):

         return True


    def WritePWM(self,ioPin,value):

        return True


    def WritePin(self,ioPin,value):

        return True


    def ReadPin(self,ioPin):
        value = random.getrandbits(1)
      #  print('readpin',value)

        return value