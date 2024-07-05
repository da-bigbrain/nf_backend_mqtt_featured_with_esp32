from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np

app = Flask(__name__)
CORS(app)

# Assuming EEG data typically has a sampling rate of 250 Hz
sampling_rate = 250  # Hardcoded sampling rate in Hz

def apply_fft(data):
    try:
        data_np = np.array(data)  # Convert data to numpy array
        n = len(data_np)
        fft_result = np.fft.fft(data_np)  # Apply FFT
        freq = np.fft.fftfreq(n, d=1/sampling_rate)  # Frequency axis

        # Find indices corresponding to beta waves (13-30 Hz)
        beta_indices = np.where((freq >= 13) & (freq <= 30))[0]
        
        # Extract amplitudes for beta waves
        beta_amplitudes = np.abs(fft_result[beta_indices])
        
        return freq[beta_indices].tolist(), beta_amplitudes.tolist()
    except Exception as e:
        raise ValueError("Error during FFT computation: " + str(e))

@app.route('/upload_data', methods=['POST'])
def upload_data():
    try:
        data = request.json
        if 'data' in data:
            data_chunk = data['data']
            
            # Process the data_chunk as needed
            print("Received data:", data_chunk)
            
            # Apply FFT and filter beta waves
            freq, beta_amplitudes = apply_fft(data_chunk)
            if beta_amplitudes:
                avg_beta_amplitude = np.mean(beta_amplitudes)
            else:
                avg_beta_amplitude = 0  # Handle the case with no beta frequencies
            
            return jsonify({
                "status": "success", 
                "beta_wave_frequencies": freq, 
                "average_beta_amplitude": avg_beta_amplitude
            }), 200
        else:
            return jsonify({
                "status": "error", 
                "message": "Invalid data format. Expected 'data'."
            }), 400
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
