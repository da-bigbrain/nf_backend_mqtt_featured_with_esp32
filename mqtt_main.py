from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_mqtt import Mqtt
import numpy as np
import eventlet
from datetime import datetime
import json


eventlet.monkey_patch()


# Create a Flask application
app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = 'nf.enk.icu'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'inky'
app.config['MQTT_PASSWORD'] = 'asdf'
# Create a Socket.IO server with CORS enabled
socketio = SocketIO(app, cors_allowed_origins='*')
mqtt = Mqtt(app)

@app.route('/')
def index():
    return 'Socket.IO server is running.'

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# MQTT broker details
# broker = "nf.enk.icu"
# port = 1883
topic = "testTopic"
# publish_topic = "beta"
# username = "inky"
# password = "asdf"

# FFT configuration
chunk_size = 256  # example larger chunk size
sampling_rate = 1000  # Hz, change as per your requirements
beta_freq_range = (12, 30)  # Beta frequency range in Hz

data_chunk = []

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe(topic)

# Callback function on message receive
@mqtt.on_message()
def handle_mqtt_message(client, userdata, msg):
    global data_chunk
    try:
        # Log the message payload for debugging
        print(f"Received message payload (length {len(msg.payload)}): {msg.payload}")

        # Ensure the message payload is 4 bytes
        if len(msg.payload) <= 4:
            # Decode the message payload as an integer
            value = int(msg.payload.decode("utf-8"))
            data_chunk += [value] * 64
            
            print(f"Received data chunk size: {len(data_chunk)}")

            # Ensure data_chunk is the correct size
            if len(data_chunk) >= chunk_size:
                print("Performing FFT...")

                # Perform FFT
                fft_result = np.fft.fft(data_chunk[:chunk_size])
                fft_freqs = np.fft.fftfreq(chunk_size, 1/sampling_rate)

                # Find indices corresponding to beta frequency range
                beta_indices = np.where((fft_freqs >= beta_freq_range[0]) & (fft_freqs <= beta_freq_range[1]))[0]
                # Calculate average amplitude for beta range
                beta_amplitudes = [np.abs(fft_result[i]) for i in beta_indices]
                print("Filtered size:", len(beta_amplitudes), beta_amplitudes)
                avg_beta_amplitude = np.mean(beta_amplitudes)
                print("Average amplitude for beta range:", avg_beta_amplitude)

                # Emit the average beta amplitude
                data =  {'avg_beta_amplitude': avg_beta_amplitude, 'time': datetime.now()}
                socketio.emit('mqtt',  data=json.dumps(data, default=str))
                print("Emitted avg_beta_amplitude ", avg_beta_amplitude)

                # Clear data_chunk for the next set of samples
                data_chunk = data_chunk[chunk_size:]
        else:
            print(f"Received message with unexpected length: {len(msg.payload)}")
    except Exception as e:
        print(f"Error processing message: {e}")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=True)