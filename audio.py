import pyaudio
import numpy as np
import wave
import time
import datetime
import os
import librosa
from scipy.signal import butter, lfilter
from settings import THRESHOLD, HEIGHT, WIDTH

# Noise suppression functions
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def noise_suppression(input_signal, fs):
    # Bandpass filter to remove frequencies outside of the human voice range
    filtered_signal = butter_bandpass_filter(input_signal, 300, 3400, fs)
    return filtered_signal

# Feature extraction functions
def apply_fft(input_signal):
    fft_spectrum = np.fft.fft(input_signal)
    frequencies = np.fft.fftfreq(len(fft_spectrum))
    magnitude = np.abs(fft_spectrum)
    return frequencies, magnitude

def extract_mfcc(input_signal, sr=44100, n_mfcc=13):
    mfccs = librosa.feature.mfcc(y=input_signal, sr=sr, n_mfcc=n_mfcc)
    return mfccs

def feature_extraction(input_signal):
    frequencies, magnitudes = apply_fft(input_signal)
    mfccs = extract_mfcc(input_signal)
    return frequencies, magnitudes, mfccs

# Dynamic thresholding
ambient_noise_level = np.inf  # Initialize with a high value to be updated dynamically

def update_ambient_noise_level(current_audio_level):
    global ambient_noise_level
    alpha = 0.1  # Smoothing factor
    if ambient_noise_level == np.inf:
        ambient_noise_level = current_audio_level
    else:
        ambient_noise_level = alpha * current_audio_level + (1 - alpha) * ambient_noise_level

# Audio callback function with noise suppression, feature extraction, and dynamic thresholding
def audio_callback(in_data, frame_count, time_info, status, raining, audio_data, previous_audio_data, recorded_frames, is_recording, recording_start_time, p):
    current_audio_data = np.frombuffer(in_data, dtype=np.int16)
    current_audio_data = noise_suppression(current_audio_data, 44100)  # Apply noise suppression
    frequencies, magnitudes, mfccs = feature_extraction(current_audio_data)  # Feature extraction

    # Update ambient noise level when not raining
    if not raining[0]:
        update_ambient_noise_level(np.linalg.norm(mfccs))

    # Dynamic threshold for triggering events
    dynamic_threshold = ambient_noise_level * 1.5  # Dynamic threshold based on ambient noise
    if np.linalg.norm(mfccs) > dynamic_threshold:
        raining[0] = True
        if not is_recording[0]:
            is_recording[0] = True
            recorded_frames.clear()
            recording_start_time[0] = time.time()
    else:
        raining[0] = False
        audio_data.fill(0)
        if is_recording[0]:
            is_recording[0] = False
            recording_duration = time.time() - recording_start_time[0]
            if recording_duration >= 0.2:
                save_recording(recorded_frames, p)
                recorded_frames.clear()

    if is_recording[0]:
        recorded_frames.append(in_data)

    return (in_data, pyaudio.paContinue)



def get_audio_input_stream(callback_args,p):
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024, stream_callback=lambda in_data, frame_count, time_info, status: audio_callback(in_data, frame_count, time_info, status, **callback_args,p=p))
    return  stream

def save_recording(recorded_frames,p):
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    wav_filename = f"recordings/{timestamp}.wav"
    bin_filename = f"recordings/{timestamp}_binary.txt"  # Filename for binary data

    os.makedirs(os.path.dirname(wav_filename), exist_ok=True)

    # Save WAV file
    with wave.open(wav_filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(recorded_frames))
    print(f"Recording saved as {wav_filename}")

    # Convert audio bytes to binary string and save as TXT file
    with open(bin_filename, 'w') as bf:
        for frame in recorded_frames:
            # Convert each byte to binary and write to file
            bits = ''.join(f'{byte:08b}' for byte in frame)
            bf.write(bits + '\n')
    print(f"Binary data saved as {bin_filename}")


def generate_and_save_keys(encryption_option, limit):
    directory_name = f"{encryption_option}bit CNK"
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    for i in range(limit or 1):  # If limit is 0, generate at least one key
        key_data = "Your key generation logic here"
        file_name = f"{directory_name}/{encryption_option}bit.{date_str}.{i}.ky"
        with open(file_name, 'w') as file:
            file.write(key_data)


def record_and_save_bits(encryption_option, limit, p):
    bit_length = int(encryption_option.replace('bit', ''))
    directory_name = f"{encryption_option} CNK"
    os.makedirs(directory_name, exist_ok=True)
    
    # Prepare to record
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
    print(f"Recording for {limit} files of {bit_length} bits each.")
    
    for i in range(limit):
        bits_collected = 0
        bits = ''
        while bits_collected < bit_length:
            data = stream.read(1024)
            # Convert to bits
            frame_bits = ''.join(f'{byte:08b}' for byte in data)
            bits += frame_bits
            bits_collected += len(frame_bits)
        
        # Trim to exact bit length needed and save
        bits = bits[:bit_length]
        file_name = f"{directory_name}/{encryption_option}.{i}.bits"
        with open(file_name, 'w') as file:
            file.write(bits)
        print(f"Bits saved as {file_name}")
    
    stream.stop_stream()
    stream.close()
    print("Completed recording and saving bits.")

