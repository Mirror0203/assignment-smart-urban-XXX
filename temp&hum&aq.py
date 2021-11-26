## This example uses the blue colored DHT sensor connected to D2.
import grovepi
import time

dhtSensor = 2  # The (digital humidity & temperature) Sensor goes on digital port 2.

air_sensor = 0
grovepi.pinMode(air_sensor,"INPUT")
local_time0=time.localtime(time.time())
dt0=time.strftime('%Y-%m-%d %H:%M:%S',local_time0)
sleeptime=5

runtime=100
print('start sleeping at',dt0,'for',sleeptime,'seconds')
time.sleep(sleeptime)

blue = 0    # The Blue colored sensor.
local_time1=time.localtime(time.time())
dt1=time.strftime('%Y-%m-%d %H:%M:%S',local_time1)
print('stop sleeping at',dt1,'start running for',runtime,'seconds')

temp_list=[]
humid_list=[]
aq_list=[]
timeout=time.time() +runtime
numberofdata=0
while True:
    try:
        [temp,humidity] = grovepi.dht(dhtSensor, blue)
        temp_list.append(temp)
        humid_list.append(humidity)
        numberofdata=numberofdata+1
        print(numberofdata)
        print("temp = %.02f C humidity =%.02f%%" % (temp, humidity))
        aq_value = grovepi.analogRead(air_sensor)
        print('the value of air  quality is:',aq_value)
        aq_list.append(aq_value)
        time.sleep(1) # Wait 1 sec before nex readout 
    except Exception as e:
        print ("Error: "+str(e)) 
    
    if time.time()>timeout:
        break
    
local_time2=time.localtime(time.time())
dt2=time.strftime('%Y-%m-%d %H:%M:%S',local_time2)
print('')
print('start at',dt1,'and end at',dt2)
print('the number of the data been recorded is',numberofdata,'the system collected data for',runtime,'seconds')
print('temperature (C):',temp_list)
print('air quality value (%):',aq_list)
#print('concentration (pcs/0.01cf) :',dust_list)

