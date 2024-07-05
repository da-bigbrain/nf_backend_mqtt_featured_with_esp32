import paho.mqtt.client as mqtt
import numpy as np
from struct import unpack

# MQTT broker details
broker = "nf.enk.icu"
port = 1883
topic = "testTopic"
publish_topic = "beta"
username = "inky"
password = "asdf"

# FFT configuration
chunk_size = 1024
sampling_rate = 1000  # Hz, change as per your requirements
beta_freq_range = (12, 30)  # Beta frequency range in Hz

data_chunk = []

# Callback function on message receive
def on_message(client, userdata, msg):
    global data_chunk
    try:
        # Log the message payload for debugging
        print(f"Received message payload (length {len(msg.payload)}): {msg.payload}")

        # Ensure the message payload is 4 bytes
        if len(msg.payload) == 4:
            # Decode the message payload as a float
            value = unpack('f', msg.payload)[0]
            data_chunk.append(value)
            
            print(f"Received data chunk size: {len(data_chunk)}")

            # Ensure data_chunk is the correct size
            if len(data_chunk) == chunk_size:
                print("Performing FFT...")

                # Perform FFT
                fft_result = np.fft.fft(data_chunk)
                fft_freqs = np.fft.fftfreq(chunk_size, 1/sampling_rate)

                # Find indices corresponding to beta frequency range
                beta_indices = np.where((fft_freqs >= beta_freq_range[0]) & (fft_freqs <= beta_freq_range[1]))[0]

                # Calculate average amplitude for beta range
                beta_amplitudes = [np.abs(fft_result[i]) for i in beta_indices]
                avg_beta_amplitude = np.mean(beta_amplitudes)
                print("Average amplitude for beta range:", avg_beta_amplitude)





                # Publish the average beta amplitude
                client.publish(publish_topic, avg_beta_amplitude)

                # Clear data_chunk for the next set of samples
                data_chunk = []
        else:
            print(f"Received message with unexpected length: {len(msg.payload)}")
    except Exception as e:
        print(f"Error processing message: {e}")

# Create an MQTT client instance
client = mqtt.Client()

# Set username and password
client.username_pw_set(username, password)

# Attach the message receive callback function
client.on_message = on_message

# Connect to the broker
client.connect(broker, port)

# Subscribe to the topic
client.subscribe(topic)

# Start the loop to process callbacks and handle reconnections
client.loop_forever()
