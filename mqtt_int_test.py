import paho.mqtt.client as mqtt
import struct

# MQTT broker details
broker = "104.237.153.38"
port = 1883
topic = "testTopic"
publish_topic = "beta"
username = "inky"
password = "asdf"


# Callback function to handle incoming messages
def on_message(client, userdata, message):
    try:
        # Decode message payload
        payload = message.payload.decode("utf-8")

        # Check if payload is a string that represents an integer
        if payload.isdigit():
            # Convert string to integer using struct.unpack
            # Assuming the payload is exactly 4 bytes for the purpose of unpacking
            # Adjust this as needed based on the actual payload structure
            integer_value = int(message.payload.decode("utf-8"))
            # print()

            print(f"Converted integer: {int(message.payload.decode('utf-8'))}")
            # Publish the converted integer to another topic
            client.publish(publish_topic, str(integer_value))
        else:
            print(f"Received string is not a digit: {payload}")
    except Exception as e:
        print(f"Error: {e}")


# Set up MQTT client
client = mqtt.Client()
client.username_pw_set(username, password)
client.on_message = on_message

# Connect to the MQTT broker
client.connect(broker, port, 60)

# Subscribe to the topic
client.subscribe(topic)

# Start the loop to process received messages
client.loop_forever()
