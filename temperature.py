#!/usr/bin/python3
import os
import glob
import time
from datetime import datetime
import paho.mqtt.client as mqtt

from config import BROKER_ADDR, MQTT_TOPIC, MQTT_STATUS, MQTT_TEMP

TEMP_TOPIC = "/".join((MQTT_TOPIC, MQTT_TEMP))
STATUS_TOPIC = "/".join((MQTT_TOPIC, MQTT_STATUS))

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def on_connect(client, userdata, flags, rc):
    print("Connected with result code: {}".format(rc))
    client.publish(topic=STATUS_TOPIC, payload="Online", qos=0, retain=True)	

def on_disconnect(client, userdata, rc):
    print("Client got disconnected")

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.will_set(topic=STATUS_TOPIC, payload="Offline", qos=0, retain=True)
client.connect(BROKER_ADDR)

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

client.loop_start()
while True:
    temp_c = read_temp()
    temp_f = int(round(temp_c * 9.0 / 5.0 + 32.0,2)*2)/2.0
    client.publish(topic=TEMP_TOPIC, payload=temp_f, qos=0, retain=True)
    now = datetime.now()
    print(now.strftime("%d/%m/%Y %H:%M:%S"),'temperature (F)', temp_f)
    time.sleep(60)

#client.disconnect()
