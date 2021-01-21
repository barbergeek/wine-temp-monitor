import os
import glob
import time
from datetime import datetime
import paho.mqtt.client as mqtt

from config import BROKER_ADDR, MQTT_TOPIC

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

mqtt_client = mqtt.Client("wine-temp")

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

while True:
    temp_c = read_temp()
    temp_f = round(temp_c * 9.0 / 5.0 + 32.0,2)
    mqtt_client.connect(BROKER_ADDR)
    mqtt_client.publish(MQTT_TOPIC, temp_f)
    mqtt_client.disconnect()
    now = datetime.now()
    print(now.strftime("%d/%m/%Y %H:%M:%S"),'temperature (F)', temp_f)
    time.sleep(60)

