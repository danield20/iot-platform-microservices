import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
import sys
import time
import json
import datetime
import os

client_mqtt = None
client_influxdb = None
printing = False

def is_number(x):
    if type(x) == int or type(x) == float:
        return True
    return False

def on_connect(client, userdata, flags, rc):
    if printing:
        print("Connected to mqtt " + str(rc), flush=True)
    client_mqtt.subscribe("#")

def on_disconnect(client, userdata, rc=0):
    if printing:
        print("Disconnected from mqtt " + str(rc), flush=True)
    client_mqtt.loop_stop()

def on_message(client, userdata, msg):
    # compose the tags field
    tags = {}
    string_list = msg.topic.split("/")
    tags["location"] = string_list[0]
    tags["device"] = string_list[1]

    # make points
    json_string = str(msg.payload, 'utf-8')
    sent_measurements = json.loads(json_string)
    realtime = str(datetime.datetime.now())
    time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    if printing:
        print(realtime + ": Received a message by topic: " + msg.topic, flush=True)
    if "timestamp" in sent_measurements:
        time = sent_measurements["timestamp"]
        if printing:
            print(realtime + ": Data timestamp is " + time, flush=True)
    else:
        if printing:
            print(realtime + ": Data timestamp is NOW", flush=True)

    current_points = []
    for k in sent_measurements:
        if is_number(sent_measurements[k]):
            current_point = {}
            current_point["measurement"] = k
            current_point["tags"] = tags
            current_point["time"] = time
            current_point["fields"] = {"value":sent_measurements[k]}
            if printing:
                print(realtime + ": " + msg.topic.replace("/",".") + "." + k + " = " + str(sent_measurements[k]), flush=True)
            current_points.append(current_point)

    if (client_influxdb.write_points(current_points)):
        if printing:
            print(realtime + ": Series added", flush=True)
    else:
        if printing:
            print(realtime + ": Series not added", flush=True)

def connect_to_mqtt():
    global client_mqtt
    client_mqtt = mqtt.Client()
    client_mqtt.on_connect = on_connect
    client_mqtt.on_message = on_message

    client_mqtt.connect("mqtt", 1883, 60)

    client_mqtt.loop_start()

    while(True):
        continue

def connect_to_db():
    global client_influxdb
    client_influxdb = InfluxDBClient(host="influxdb", port=8086)

    exists = False
    for d in client_influxdb.get_list_database():
        if d["name"] == "iot_devices":
            exists = True
            break

    if not exists:
        client_influxdb.create_database("iot_devices")
        if printing:
            print("Database created", flush=True)

    client_influxdb.switch_database("iot_devices")

def main():
    global printing
    if "DEBUG_DATA_FLOW" in os.environ:
        printing = (os.environ["DEBUG_DATA_FLOW"] == "True")
    time.sleep(5)
    connect_to_db()
    connect_to_mqtt()

if __name__ == "__main__":
    main()