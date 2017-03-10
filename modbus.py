
import minimalmodbus
from influxdb import InfluxDBClient
import json
import time

USER = 'openhab'
PASSWORD = 'habopen'
DBNAME = 'openhabDB'
host = '192.168.2.201'
port = 8086

data = {}

instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 3) # port name, slave address (in decimal)
instrument.serial.baudrate = 9600   # Baud
instrument.serial.timeout  = 0.8   # seconds
instrument.debug = True
print(instrument)
series = []



#data['SYSTEM-ID'] = instrument.read_string(0x04b6, 8)
#data['STROM1'] = instrument.read_register(0x1,2)
data['STROM1'] = instrument.read_register(0x1,2)
data['STROM2'] = instrument.read_register(0x2,2)
data['STROM3'] = instrument.read_register(0x3,2)
data['STROM4'] = instrument.read_register(0x4,2)
data['STROM5'] = instrument.read_register(0x5,2)
data['STROM6'] = instrument.read_register(0x6,2)
data['STROM7'] = instrument.read_register(0x7,2)
data['STROM8'] = instrument.read_register(0x8,2)
data['STROM9'] = instrument.read_register(0xC,2)
data['STROM10'] = instrument.read_register(0xD,2)
#data['STROM4'] = instrument.read_register(0x89,1)
data['TEMPERATUR1'] = instrument.read_register(0x4A0,0,signed=True)

for key,value in data.items():
    series = []

    body ={
        "measurement": key,
   #     "tags": {
    #        "STRING": key,
     #   },
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "fields": {
           "value": value,
        }
    }
    series.append(body)
    print('xxx',series)

    client = InfluxDBClient(host, port, USER, PASSWORD, DBNAME)
    #print("Write points #: {0}".format(total_records))
    client.write_points(series, retention_policy='autogen')

#jsonarray = json.dumps(data)
#print('Data',jsonarray)

#minimalmodbus._print_out('Temperatur1: ' +str(instrument.read_register(0x9,3,signed=True)))
#minimalmodbus._print_out('Voltage: ' +str(instrument.read_register(0xA,1,)))


#print (temperature)
#print (strom1)
#print (strom2)
#print (name)

## Change temperature setpoint (SP) ##
#NEW_TEMPERATURE = 95
#instrument.write_register(24, NEW_TEMPERATURE, 1) # Registernumber, value, number of decimals for storage

#mqttc = mqtt.Client('python_pub')
#mqttc.connect('192.168.2.50', 1883)
#mqttc.publish('/MODBUS', jsonarray)
#mqttc.loop(2)