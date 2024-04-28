import pyaudio
import numpy as np
import wave
import time
import datetime
import os

from settings import THRESHOLD, HEIGHT, WIDTH

def audio_callback(in_data, frame_count, time_info, status, raining, audio_data, previous_audio_data, recorded_frames, is_recording, recording_start_time, p):
    current_audio_data = np.frombuffer(in_data, dtype=np.int16)
    # Normalize current audio data for display
    current_audio_data = np.interp(current_audio_data, (current_audio_data.min(), current_audio_data.max()), (-HEIGHT // 4, HEIGHT // 4))
    
    # Update audio_data for visualization
    audio_data[:] = (previous_audio_data + current_audio_data) / 2
    previous_audio_data[:] = current_audio_data

    # Calculate volume from current audio data for threshold detection
    volume = np.linalg.norm(current_audio_data)

    if volume > THRESHOLD:
        raining[0] = True
        if not is_recording[0]:
            is_recording[0] = True
            recorded_frames.clear()
            recording_start_time[0] = time.time()
    else:
        raining[0] = False
        audio_data.fill(0)  # Clear audio data when volume is below threshold
        if is_recording[0]:
            is_recording[0] = False
            recording_duration = time.time() - recording_start_time[0]
            if recording_duration >= 0.2:  # Save recordings longer than 0.2 seconds
                save_recording(recorded_frames, p)
                recorded_frames.clear()  # Clear recorded_frames after saving

    if is_recording[0]:
        recorded_frames.append(in_data)  # Accumulate audio data while recording

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