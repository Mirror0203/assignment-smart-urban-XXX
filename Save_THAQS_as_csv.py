"""
Created on Sat Nov 26 19:17:49 2021
@author: Mirror
"""

import grovepi
import time

output_filename = 'data_group7&8_temp&humid&AQ_testversion.csv'
header = ("Timestamp","Temperature","Humid","AQ_value","Sound_value")
strHeader = ';'.join(header)
csv_file = open(output_filename, 'a+') 
csv_file.write(strHeader + '\n') 
csv_file.close() 

## DHT-Digital2, airquality-Analog1
dhtSensor = 2 
air_sensor = 1
sound_sensor=2
grovepi.pinMode(air_sensor,"INPUT")
grovepi.pinMode(sound_sensor,"INPUT")
local_time0=time.localtime(time.time())
dt0=time.strftime('%Y-%m-%d %H:%M:%S',local_time0)
sleeptime=0
runtime=30*60
runstep=1
print('start sleeping at',dt0,'for',sleeptime,'seconds')
time.sleep(sleeptime)

blue = 0    # The Blue colored sensor.
local_time1=time.localtime(time.time())
dt1=time.strftime('%Y-%m-%d %H:%M:%S',local_time1)
print('stop sleeping at',dt1,'start running for',runtime,'seconds, data will be detected every',runstep,'seconds')


timeout=time.time() +runtime
numberofdata=0
while True:
    try:
        [temp,humidity] = grovepi.dht(dhtSensor, blue)

        numberofdata=numberofdata+1 #to know how many set of data is recorded
        print(numberofdata)
        print("temp = %.02f C humidity =%.02f%%" % (temp, humidity))
        
        aq_value = grovepi.analogRead(air_sensor)
        print('the value of air  quality is:',aq_value)
        
        sound_value=grovepi.analogRead(sound_sensor)
        print('the sound value is:',sound_value)
        
        local_timecsv=time.localtime(time.time())
        dtcsv=time.strftime('%Y-%m-%d %H:%M:%S',local_timecsv)
        ### CSV writing part BEGINNING ###
        # Format angle and sensor_value as a csv file line
        data = [str(dtcsv), str(temp), str(humidity),str(aq_value),str(sound_value)] 
        strData = ';'.join(data) 

        # Write sensor values to the csv file
        csv_file = open(output_filename, 'a+') # Again open (the same) file in 'a+' mode
        csv_file.write(strData + '\n') # Write string of joined (; separated) data & finish the line using '\n' 
        csv_file.close() # Close the file again
        ### CSV writing part END ###
        
        time.sleep(runstep)
        
    except Exception as e:
        print ("Error: "+str(e)) 
    
    #break after a certain time
    if time.time()>timeout: 
        break
    
local_time2=time.localtime(time.time())
dt2=time.strftime('%Y-%m-%d %H:%M:%S',local_time2)
print('')
print('start at',dt1,'and end at',dt2)
print('the number of the data been recorded is',numberofdata,'the system collected data for',runtime,'seconds')