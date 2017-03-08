import ujson

class tempfile(object):

    def __init__(self,filename):
        self._filename = filename

    def openfile(self):
        try:
         #   print('opem')
            with open(self._filename)as fh:
                data = ujson.loads(fh.read())
                fh.close()
			
           # fh=open(self._filename, 'r')
            #with open(self._filename)as fh:
            #data = ujson.load(fh)
            #print('test',data,fh)
            #fh.close()
        except:
            data = None
          #  print('failed')

        return data


    def writefile(self,data):
            with open(self._filename,'w')as fh:
                ujson.dump(data,fh,indent =4)

	    return True