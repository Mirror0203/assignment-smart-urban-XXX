## ##########################################################
## @title: GrovePi+ Angle sensor MQTT publish example
## @author: Milos Viktorovic
## @email: m.viktorovic@tue.nl
## @version: 2.0b [01-12-19]
## ##########################################################

## THIS EXAMPLE REQUIRES FUNCTIONAL iNTERNET CONNECTION AND ROTARY ANGLE SENSOR CONNECTED TO A0
## Code will then publish any change of the angle (bigger than 5 deg) to the MQTT
## Incoming 'control' messages will only be printed on the console

import grovepi
from time import sleep
import paho.mqtt.client as mqtt_client
import paho.mqtt.subscribe as mqtt_subscribe
import re
threshold_change=[700,300,400]
threshold_copy=threshold_change
highair_td,lowair_td,noisy_td=threshold_change
print('the default value is:' ,highair_td,lowair_td,noisy_td)
# user variables
offline = False  ## ste to True if working offline, as it allows the script to continue even if MQTT cannot connect
client_id = "StudentGroup_7&8"
mqtt_host = "broker.hivemq.com"
mqtt_port = 1883
publishing_topic = "testtopic/7ZW5M0/StudentGroup_7&8/warning"
subscription_topic = "testtopic/7ZW5M0/" + client_id + "/control"
num_of_tries_mqtt = 3  # maximum number of tries for MQTT connection

connectedFlag = False  # tracks if client is connected
subscribedFlag = False  # tracks if client is subscribed to a topic


# MQTT function on_message https://pypi.org/project/paho-mqtt/#subscribe-unsubscribe
def on_message(client, userdata, message):
    global threshold_change,threshold_copy,highair_td,lowair_td,noisy_td
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print("Received message '" + str(message.payload) + "' on topic '"
          + message.topic + "' with QoS " + str(message.qos))
    print(message.payload)
    change=message.payload.decode()
    #print(change)
    threshold_change=[int(s) for s in re.findall(r'\b\d+\b', change)]
    #print(threshold_change)
    if threshold_change!=threshold_copy:
        msg_0='the threshold is changed to :'+str(threshold_change)
        print(msg_0)
        threshold_copy=threshold_change
        highair_td,lowair_td,noisy_td=threshold_change
        print(highair_td,lowair_td,noisy_td)
        mqtt.publish(topic='threshold changed',
                             payload=msg_0,
                             qos=2
                             )
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")


def on_subscribe(client, userdata, mid, granted_qos):
    global subscribedFlag  ## Global required in order to be able to make changes
    subscribedFlag = True
    print(client, " subscribed!")


def on_unsubscribe(client, userdata, mid):
    global subscribedFlag
    subscribedFlag = False
    print(client, " unsubscribed!")


def on_connect(client, userdata, flags, rc):
    global connectedFlag
    connectedFlag = True
    print(">>>>>>>>>> Sucess! MQTT connected! >>>>>>>>>>>")


def on_disconnect(client, userdata, rc):
    global connectedFlag
    connectedFlag = False
    print(">>>>>>>>>> Attention! MQTT disconnected! >>>>>>>>>>>")
    print(" Trying to reconnect!")
    try_to_connect_and_subscribe(client_id, mqtt_host, mqtt_port, max_num_of_attempts=num_of_tries_mqtt,
                                 topic=subscription_topic)


def try_to_connect_and_subscribe(client_id, mqtt_host, mqtt_port, max_num_of_attempts=1, topic='testtopic/#',
                                 qos=2):  # Tries to connect to MQTT server # Returns Client class on sucess or FALSE on fail.

    mqtt = False

    while max_num_of_attempts > 0:
        try:
            # print("Trying to connect to MQTT")

            # creating MQTT client
            mqtt = mqtt_client.Client(client_id)
            print("DEBUG: Client created!")

            mqtt.on_connect = on_connect
            mqtt.on_disconnect = on_disconnect
            mqtt.on_subscribe = on_subscribe
            mqtt.on_unsubscribe = on_unsubscribe
            mqtt.on_message = on_message  # define function that executes on message arrival
            # connecting to MQTT server

            print("DEBUG: Attempting to connect")
            mqtt.connect(host=mqtt_host, port=mqtt_port)
            print("DEBUG: MQTT connected!")

            mqtt.loop_start()  # runs the network loop
            global connectedFlag
            connectedFlag = True  # sets the connection flag

            print("DEBUG: Trying to subscribe to '" + topic + "'")
            mqtt.subscribe(topic, qos)  # subscribes to the desired topic
            sleep(3)

            return mqtt
            break  # exit loop if connection established

        except:
            print("MQTT connection error!")
            mqtt = False
            # print("Check your network connectivity and MQTT setings!")
            # exit()

        max_num_of_attempts -= 1
        print("Attempts left: ", max_num_of_attempts)
        print("--->")
        sleep(5)  # 5sec inbetween connection attempts


# Sensor initialization variables
potentiometer = 0;# Rotary Angle sensor must be connected to A0
# dhtSensor = 2
air_sensor = 1
sound_sensor = 2
grovepi.pinMode(potentiometer, "INPUT")
grovepi.pinMode(air_sensor, "INPUT")
grovepi.pinMode(sound_sensor, "INPUT")

sleep(2)  # let the board load commands

### Starting main part of the script!
print("### Script Started! ###")

# Trying to connect to mqtt server

if not offline:

    mqtt = try_to_connect_and_subscribe(client_id, mqtt_host, mqtt_port, max_num_of_attempts=num_of_tries_mqtt,
                                        topic=subscription_topic)
    if mqtt == False:
        print("MQTT connection error!")
        print("Check your network connectivity and MQTT setings!")

        if offline:
            print("Attention! Offline mode activated, script will continue")
        else:
            print("Attention! Offline mode not activated, script will terminate")
            print(">>> Script Terminating!!!")
            exit()

        # Pre-initialize variables for payload
msg_1 = ""
msg_2 = ''
msg_3 = ''
# msg_4 = ''
# msg_5 = ''

# preinitialise variable for storing previous values
old_angle_value = -5

# Main loop
while True:
    highair_td,lowair_td,noisy_td=threshold_change

    try:

        print("\nTrying to read sensor value")
        aq_value = grovepi.analogRead(air_sensor)
        sensor_value = grovepi.analogRead(potentiometer)
        sound_value = grovepi.analogRead(sound_sensor)
        voltage = round((float)(sensor_value) * 5 / 1023, 2)  # convert sensor readout to voltage
        degrees = round(voltage * 300 / 5, 2)  # convert voltage to angle in degrees 0-300

        print("Potentiometer value read: ", degrees, "°")
        print('the value of air  quality is:', aq_value)
        print('the sound value is:', sound_value)

        if abs(degrees - old_angle_value) > 5:  # only write if change is bigger than 5°

            print("New angle value is: ", degrees, "°")
            old_angle_value = degrees
            msg_1 = degrees

            if connectedFlag:
                print("DEBUG: Trying to publish message!")
                mqtt.publish(topic=publishing_topic,
                             payload=degrees,
                             qos=2
                             )

                # if there is a message, it will be processed through function on_message
        if aq_value > highair_td:
            msg_2='High pollution:'+str(aq_value)
            if connectedFlag:
                print("DEBUG: Trying to publish message!")
                mqtt.publish(topic=publishing_topic,
                             payload=msg_2,
                             qos=2
                             )
        elif aq_value>lowair_td:
            msg_2='Low pollution:'+str(aq_value)
            if connectedFlag:
                print("DEBUG: Trying to publish message!")
                mqtt.publish(topic=publishing_topic,
                             payload=msg_2,
                             qos=2
                             )
        else:
            msg_2='Fresh air:' + str(aq_value)
        print(msg_2)


        if sound_value>noisy_td:
            msg_3 = 'This place is too noisy:' + str(sound_value)
            if connectedFlag:
                print("DEBUG: Trying to publish message!")
                mqtt.publish(topic=publishing_topic,
                             payload=msg_3,
                             qos=2
                             )
    except:
        print("Error occured! (script is continuing)")

    sleep(2)  # wait 2sec before next readout

mqtt.loop_stop()  # stops the network loop