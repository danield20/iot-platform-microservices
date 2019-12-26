import paho.mqtt.client as mqtt
import sys
import json
import time

NAME = "Daniel"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("UPB/RPi_1/#")
    client.subscribe("UPB/RPi_2/#")

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

client.loop_start()
input()
for i in range(5):
    x = '{{ "BAT":{}, "HUMID":{}, "PRJ":"SPRC", "TMP":{}, "status":"OK"}}'.format(i*10+5, i*10+4, i*10+3.5)
    client.publish("UPB/RPi_1", qos=2, payload=x)
    time.sleep(1)

for i in range(5):
    x = '{{ "BAT":{}, "HUMID":{}, "PRJ":"SPRC", "TMP":{}, "status":"OK"}}'.format(i*20+5, i*20+4, i*20+3.5)
    client.publish("UPB/RPi_2", qos=2, payload=x)
    time.sleep(1)

while True:
    continue
