from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import time
import numpy as np

chunk_size = 512  # Number of samples per chunk
sampling_rate = 2000  # Sampling rate in Hz
beta_freq_range = (12, 30)  # Beta frequency range in Hz

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

def setup():
    print("Setup completed.")

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@app.route('/upload_data', methods=['POST'])
def upload_data():
    data = request.json.get('data')
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    data_chunk = list(map(int, data))

    # Perform FFT
    fft_result = np.fft.fft(data_chunk)
    fft_freqs = np.fft.fftfreq(chunk_size, 1/sampling_rate)

    # Find indices corresponding to beta frequency range
    beta_indices = np.where((fft_freqs >= beta_freq_range[0]) & (fft_freqs <= beta_freq_range[1]))[0]

    # Calculate average amplitude for beta range
    beta_amplitudes = [np.abs(fft_result[i]) for i in beta_indices]
    avg_beta_amplitude = np.mean(beta_amplitudes)
    print("Average amplitude for beta range:", avg_beta_amplitude)

    socketio.emit('average_amplitude', avg_beta_amplitude)
    print("Sent average amplitude to client.")

    return jsonify({'status': 'Data processed successfully'})

if __name__ == "__main__":
    setup()
    
    # Start the Flask server
    socketio.run(app, port=5001)
