# Explanation

Checkout mqtt_main.py

1. Data Collection: The script collects integer messages into data_chunk until its length reaches chunk_size.
2. FFT Processing: Once data_chunk is full, the script performs FFT and calculates the average amplitude in the beta frequency range.
3. Publishing Results: It publishes avg_beta_amplitude to the beta topic and resets data_chunk for the next set of messages.
