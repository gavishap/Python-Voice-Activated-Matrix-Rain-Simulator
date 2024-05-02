import pyaudio
import numpy as np
import wave
import time
import datetime
import os
import librosa
import webrtcvad
from scipy.signal import butter, lfilter

import pygame
from settings import THRESHOLD, HEIGHT, WIDTH
import noisereduce as nr
# Initialize VAD
vad = webrtcvad.Vad(2)  # Mode can be set to 0, 1, 2, or 3.

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
    # Apply bandpass filtering to maintain a broader human voice frequency range
    filtered_signal = butter_bandpass_filter(input_signal, 200, 4000, fs, order=5)
    # Apply noise reduction
    reduced_noise_signal = nr.reduce_noise(y=filtered_signal, sr=fs)
    return reduced_noise_signal


def resample_audio(input_signal, orig_sr, target_sr=16000):
    # Convert audio to floating-point format
    input_signal = input_signal.astype(np.float32) / 32768.0  # Convert int16 to float
    return librosa.resample(y=input_signal, orig_sr=orig_sr, target_sr=target_sr)

def is_speech(audio_data, sample_rate):
    frame_length = int(sample_rate * 0.01)  # 10 ms frame
    if len(audio_data) < frame_length:
        return False  # Or handle this case differently depending on your needs

    # Ensure the frame length is correct
    audio_frame = audio_data[:frame_length]  # Take the first 10 ms of audio
    # Convert the audio to bytes for webrtcvad
    audio_frame_bytes = np.int16(audio_frame * 32767).tobytes()
    return vad.is_speech(audio_frame_bytes, sample_rate)

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

# Dynamic thresholding and ambient noise level management
ambient_noise_level = np.inf  # Initialize with a high value to be updated dynamically

def amplify_audio(signal, factor=1000000):  # Adjust the factor to a reasonable level
    return np.abs(signal) * factor  # Use absolute value for visualization


def update_ambient_noise_level(current_audio_level):
    global ambient_noise_level
    alpha = 0.05  # Lower the smoothing factor to make it more responsive
    if ambient_noise_level == np.inf:
        ambient_noise_level = current_audio_level
    else:
        ambient_noise_level = alpha * current_audio_level + (1 - alpha) * ambient_noise_level

def audio_callback(in_data, frame_count, time_info, status, raining, audio_data, previous_audio_data, recorded_frames, is_recording, recording_start_time, p):
    print("Frame count:", frame_count)
    current_audio_data = np.frombuffer(in_data, dtype=np.int16)
    print("Original data (first 10 samples):", current_audio_data[:10])

    # Convert and resample audio data
    current_audio_data_float = current_audio_data.astype(np.float32) / 32768
    resampled_audio_data = resample_audio(current_audio_data_float, 44100, 16000)
    print("Pre-suppression (max, min):", np.max(resampled_audio_data), np.min(resampled_audio_data))

    # Apply noise suppression
    suppressed_audio_data = noise_suppression(resampled_audio_data, 16000)
    print("Post-suppression (max, min):", np.max(suppressed_audio_data), np.min(suppressed_audio_data))

    # Normalize the suppressed data for visualization
    max_amplitude = np.max(np.abs(suppressed_audio_data))  # Find the maximum amplitude
    normalized_audio_data = suppressed_audio_data / max_amplitude  # Normalize the data
    print("Normalized audio data (first 10 samples):", normalized_audio_data[:10])

    # New strategy for distributing data evenly
    if len(normalized_audio_data) < len(audio_data):
        repeat_factor = len(audio_data) // len(normalized_audio_data)
        repeated_data = np.tile(normalized_audio_data, repeat_factor)
        remaining_slots = len(audio_data) - len(repeated_data)
        audio_data[:] = np.concatenate([repeated_data, normalized_audio_data[:remaining_slots]])
    else:
        audio_data[:] = normalized_audio_data[:len(audio_data)]
    print("Length of normalized_audio_data:", len(normalized_audio_data))
    print("First 10 samples of audio_data after update:", audio_data[:10])

    # Check if the current frame contains speech
    if is_speech(normalized_audio_data, 16000):
        print("Speech detected.")
        # Calculate the current audio level
        current_audio_level = np.linalg.norm(suppressed_audio_data)
        print("Current audio level:", current_audio_level)

        # Update ambient noise level based on current audio if not raining
        if not raining[0]:
            update_ambient_noise_level(current_audio_level)
        print("Ambient noise level:", ambient_noise_level)

        # Calculate dynamic threshold based on ambient noise
        dynamic_threshold = ambient_noise_level * 1.1
        print("Dynamic threshold:", dynamic_threshold)

        # Check if the current noise level exceeds the dynamic threshold
        if current_audio_level > dynamic_threshold:
            raining[0] = True
            if not is_recording[0]:
                is_recording[0] = True
                recorded_frames.clear()
                recording_start_time[0] = time.time()
                print("Recording started.")
            recorded_frames.append(in_data)
        else:
            raining[0] = False
            audio_data.fill(0)
            if is_recording[0]:
                is_recording[0] = False
                recording_duration = time.time() - recording_start_time[0]
                print("Recording stopped, duration:", recording_duration)
                if recording_duration >= 0.2:  # Save recordings longer than 0.2 seconds
                    save_recording(recorded_frames, p)
                    recorded_frames.clear()
                    print("Recording saved.")
    else:
        print("Non-speech audio detected.")
        audio_data.fill(0)  # Mute the audio if it's not speech

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


def record_and_save_bits(encryption_option, p,limit=0):
    bit_length = int(encryption_option.replace('bit', ''))
    directory_name = f"{encryption_option} CNK"
    os.makedirs(directory_name, exist_ok=True)
    
    # Prepare to record
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
    if limit == 0:
        print(f"Recording continuously for files of {bit_length} bits each.")
    else:
        print(f"Recording for {limit} files of {bit_length} bits each.")
    
    i = 0
    last_click_time = None
    double_click_threshold = 500  # milliseconds for double click detection
    try:
        while limit == 0 or i < limit:
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
            i += 1

            # Check for double click to stop recording
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if last_click_time and pygame.time.get_ticks() - last_click_time < double_click_threshold:
                        raise KeyboardInterrupt("Double click detected, stopping recording.")
                    last_click_time = pygame.time.get_ticks()
    except KeyboardInterrupt as e:
        print(str(e))
    
    stream.stop_stream()
    stream.close()
    print("Completed recording and saving bits.")
