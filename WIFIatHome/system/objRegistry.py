
class objRegistry(object):
    def __init__(self):
        self._objRegister = {}

    def register(self,name,obj):
        self._objRegister[name]=obj

    def getObject(self,name):
        return self._objRegister.get(name,None)



