import json
import paho.mqtt.client as mqtt

latest_data = {}

def on_message(client, userdata, msg):
    global latest_data

    topic = msg.topic
    payload = json.loads(msg.payload.decode())

    latest_data[topic] = payload

client = mqtt.Client()

client.on_message = on_message

client.connect("localhost",1883)

client.subscribe("brauanlage/#")

client.loop_start()
