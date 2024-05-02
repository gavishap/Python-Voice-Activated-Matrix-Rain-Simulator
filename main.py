import pygame
import numpy as np
import random
import pyaudio 
from settings import WIDTH, HEIGHT, FONT_SIZE
from audio import get_audio_input_stream, save_recording,generate_and_save_keys, record_and_save_bits
from drawing import draw_waveform
from game_elements import Column
from menu import main_menu, cyberbit_mode_config

def main():
    pygame.init()
    pygame.font.init()  # Ensure the font module is initialized
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Matrix Rain with Audio Interaction")

    p = pyaudio.PyAudio()
     # Main menu selection
    mode = main_menu(screen)
    if mode == "cyberbit":
        option, limit = cyberbit_mode_config(screen)
        if limit is None or limit == 0:
            print("No limit provided or limit is zero, exiting.")
            pygame.quit()
            return
        limit = int(limit)
        # Start recording and saving bits
        record_and_save_bits(option, p, limit)
        pygame.quit()
        return
    # Initialize game variables
    columns = [Column(random.randint(0, WIDTH), random.randint(-HEIGHT, 0)) for _ in range(30)]
    raining = [False]  # Using list to maintain reference in callback
    audio_data = np.zeros(1024)
    previous_audio_data = np.zeros(1024)
    recorded_frames = []
    is_recording = [False]
    recording_start_time = [0]

    # Setup audio
    p = pyaudio.PyAudio()  # Create the PyAudio instance here
    callback_args = {
        'raining': raining,
        'audio_data': audio_data,
        'previous_audio_data': previous_audio_data,
        'recorded_frames': recorded_frames,
        'is_recording': is_recording,
        'recording_start_time': recording_start_time
    }
    stream = get_audio_input_stream(callback_args, p)  # Directly get the stream without unpacking

    # Start the stream
    stream.start_stream()

    running = True
    clock = pygame.time.Clock()
    last_click_time = None
    double_click_threshold = 500  # milliseconds for double click detection

    while running:
        screen.fill((0, 0, 0))

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if last_click_time and pygame.time.get_ticks() - last_click_time < double_click_threshold:
                    running = False
                    pygame.quit()
                    return
                last_click_time = pygame.time.get_ticks()

        # Update game elements
        split_screen = False  # Placeholder for split_screen logic
        # Draw audio waveform first
        draw_waveform(screen, audio_data, raining[0], split_screen)
        # Then draw columns on top of the waveform
        for col in columns:
            col.update(raining[0], split_screen)
            col.draw(screen, split_screen)

        # Display updates
        pygame.display.flip()

        # Record audio if necessary
        if not is_recording[0] and recorded_frames:
            save_recording(recorded_frames, p)
            recorded_frames.clear()

        clock.tick(20)  # Maintain 60 FPS

    # Cleanup
    stream.stop_stream()
    stream.close()
    p.terminate()
    pygame.quit()

if __name__ == "__main__":
    main()
