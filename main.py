import pygame
import random
import pyaudio
import numpy as np
import wave
import time
import datetime
import os
# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FONT_SIZE = 20
FONT = pygame.font.Font(None, FONT_SIZE)
BASE_SPEED = 8
THRESHOLD = 1500  # Increase sensitivity

# Colors
BLACK = (0, 0, 0)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 100, 255)
PINK = (255, 105, 180)
NEON_BLUE = (4, 217, 255)
WHITE = (255, 255, 255)

class Column:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = random.uniform(1, 10)  # Decrease speed for slower movement
        self.speed_increase = 0.2  # Amount to increase speed by
        self.initial_font_size = random.randint(17, 20)  # Random font size for each column
        self.font_size = self.initial_font_size
        self.should_grow = random.choice([True, False]) 
        self.font = pygame.font.Font('Halftone Font.ttf', self.font_size)  # Use custom font
        self.symbols = [random.choice(["0", "1"]) for _ in range(random.randint(4, 10))]
        self.growth_timer = pygame.time.get_ticks()

    def draw(self, screen, split_screen):
        for i, s in enumerate(self.symbols):
            # Choose color
            color = WHITE if random.random() < 0.2 else DARK_BLUE  # Glowing effect for some numbers
            label = self.font.render(s, 1, color)
            label_surface = pygame.Surface(label.get_size(), pygame.SRCALPHA)
            alpha = max(255 - int((self.y / HEIGHT) * 255 * 1.5), 0)  # Adjust the 255 and 2 to control the speed of fading
            label_surface.set_alpha(alpha)  # Set alpha value for the entire surface
            label_surface.blit(label, (0, 0))
            
            if split_screen:
                screen.blit(label_surface, (self.x + WIDTH // 2, self.y + i * self.font_size * 0.7))  # Adjust x position for split screen
            else:
                screen.blit(label_surface, (self.x, self.y + i * self.font_size * 0.7))  # Adjust y position based on a proportion of the font size
    def update(self, raining, split_screen):
        self.y += self.speed
        self.speed += self.speed_increase  # Increase speed
        # Determine which quarter of the screen the column is in and adjust x position accordingly
        if split_screen:
            effective_width = WIDTH // 2
        else:
            effective_width = WIDTH

        if self.x < effective_width / 2:  # Left half
            if self.x < effective_width / 4:  # Leftmost quarter
                self.x -= 2  # Move left at a faster speed
            else:  # Second leftmost quarter
                self.x -= 1  # Move left at a slower speed
        else:  # Right half
            if self.x < 3 * effective_width / 4:  # Second rightmost quarter
                self.x += 1  # Move right at a slower speed
            else:  # Rightmost quarter
                self.x += 2  # Move right at a faster speed

        if self.y - len(self.symbols) * self.font_size > HEIGHT and raining:  # Adjust y position based on font size and check if it's raining
            if split_screen:
                self.x = random.randint(effective_width // 2, effective_width)  # Adjust x position to a random value in the right half of the screen
            else:
                self.x = random.randint(0, effective_width)  # Adjust x position to a random value
            self.y = random.randint(-HEIGHT, -self.font_size)  # Adjust y position based on font size
            self.symbols = [random.choice(["0", "1"]) for _ in range(random.randint(4, 10))]
            self.font_size = self.initial_font_size  # Reset font size to initial size
            self.font = pygame.font.Font('Halftone Font.ttf', self.font_size)  # Create new font with reset size
            self.speed = random.uniform(1, 10)  # Reset speed
        if self.should_grow:
            if pygame.time.get_ticks() - self.growth_timer > 40 and self.font_size < 40:  # Increase size every 0.1 second, up to a maximum size of 100
                self.font_size += 1
                self.font = pygame.font.Font('Halftone Font.ttf', self.font_size)  # Create new font with increased size
                self.growth_timer = pygame.time.get_ticks()



def get_audio_input_stream(callback):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024, stream_callback=callback)
    return p, stream

def draw_waveform(screen, audio_data, raining, split_screen):
    if split_screen:
        screen = pygame.Surface((WIDTH // 2, HEIGHT))  # Create a new surface for the left half of the screen

    num_circles = 50  # Number of circles
    step_size = (WIDTH // 2 if split_screen else WIDTH) // num_circles + 2  # Calculate step size for 50 circles and add 2 for the gap
    radius = step_size // 2 - 2  # Radius of the circles, subtract 2 for the gap
    glow_colors = [NEON_BLUE, WHITE, WHITE, WHITE, WHITE]  # Colors for the glow effect

    if raining:
        for i in range(num_circles):  # Draw 50 circles
            height = min(abs(audio_data[i * (len(audio_data) // num_circles)]) * 2.5*0.5, HEIGHT)  # Multiply by 2.5 for higher amplitude
            y = max(0, HEIGHT//2 - height//2)  # Ensure y is never less than 0
            for j, color in enumerate(glow_colors):  # Draw multiple ellipses for the glow effect
                pygame.draw.ellipse(screen, color, (i * step_size + 2 + j, y + j, radius*2 - 2*j, height - 2*j))  # Draw ellipse
  

def draw_button(screen, text, position, size, color, mouse_pos):
    pygame.draw.rect(screen, color, (*position, *size))
    font = pygame.font.Font(None, 30)
    text_surf = font.render(text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=(position[0] + size[0] / 2, position[1] + size[1] / 2))
    screen.blit(text_surf, text_rect)
    return position[0] <= mouse_pos[0] <= position[0] + size[0] and position[1] <= mouse_pos[1] <= position[1] + size[1]

def get_user_input(screen, prompt):
    user_input = ''
    base_font = pygame.font.Font(None, 32)
    input_rect = pygame.Rect(WIDTH / 2 - 100, HEIGHT / 2, 140, 32)
    color_active = pygame.Color('lightskyblue3')
    color_passive = pygame.Color('gray15')
    color = color_passive
    active = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_passive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return user_input
                    elif event.key == pygame.K_BACKSPACE:
                        user_input = user_input[:-1]
                    else:
                        user_input += event.unicode

        screen.fill((0, 0, 0))
        text_surface = base_font.render(prompt + user_input, True, (255, 255, 255))
        screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        pygame.draw.rect(screen, color, input_rect, 2)
        pygame.display.flip()


def main_menu(screen):
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill((0, 0, 0))
        if draw_button(screen, "Simple Mode", (WIDTH / 2 - 100, HEIGHT / 2 - 60), (200, 50), (70, 130, 180), mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                return "simple"
        if draw_button(screen, "CyberBit Mode", (WIDTH / 2 - 100, HEIGHT / 2), (200, 50), (70, 130, 180), mouse_pos):
            if pygame.mouse.get_pressed()[0]:
                return "cyberbit"
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit()


def cyberbit_mode_config(screen):
    encryption_options = ["128bit", "256bit", "512bit", "1024bit"]
    selected_option, limit = None, None
    while selected_option is None:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill((0, 0, 0))
        for i, option in enumerate(encryption_options):
            if draw_button(screen, option + " CyberKeys Encryption", (WIDTH / 2 - 100, 100 + i * 60), (200, 50), (70, 130, 180), mouse_pos):
                if pygame.mouse.get_pressed()[0]:
                    selected_option = option
                    break
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    limit = get_user_input(screen, "Enter limit quantity (0 for no limit): ")
    return selected_option, int(limit) if limit.isdigit() else 0


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

recording_counter = 0
background_noise = None
background_noise_duration = 5 



def main():
    pygame.init()  # Initialize all imported pygame modules
    screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Set up the window for display
    pygame.display.set_caption('Matrix Rain with Voice Waveform and Audio Recording')  # Set the current window caption
    clock = pygame.time.Clock()  # Create an object to help track time

    # Mode selection
    mode = main_menu(screen)  # Display the main menu and get the selected mode
    bit_option, max_files, bit_limit = None, None, None  # Initialize variables for cyberbit mode configuration

    if mode == "cyberbit":
        bit_option, max_files = cyberbit_mode_config(screen)  # Get cyberbit mode configuration
        bit_limit = int(bit_option.replace('bit', '')) * 8  # Calculate the bit limit from the selected option
        print(f"CyberBit Mode selected with option {bit_option} and limit {max_files} files")
    else:
        print("Simple Mode selected")  # Print the selected mode if not cyberbit

    # Common setup for both modes
    audio_buffer = b''  # Initialize an empty byte string for audio buffer
    columns = [Column(x, random.randint(-HEIGHT, -FONT_SIZE)) for x in range(0, WIDTH, 15)]  # Create matrix rain columns
    raining = False  # Initialize raining effect as False
    audio_data = np.array([0]*WIDTH)  # Initialize audio data array with zeros
    previous_audio_data = np.array([0]*1024)  # Initialize previous audio data array with zeros

    split_screen = False  # Initialize split screen mode as False
    is_recording = False  # Initialize recording state as False
    recorded_frames = []  # Initialize list to store recorded frames
    recording_counter = 0  # Initialize counter for recordings

    def audio_callback(in_data, frame_count, time_info, status):
        nonlocal p,raining, audio_data, audio_buffer, previous_audio_data, is_recording, recorded_frames, recording_start_time
        audio_buffer = in_data
        current_audio_data = np.frombuffer(in_data, dtype=np.int16)
        current_audio_data = np.interp(current_audio_data, (current_audio_data.min(), current_audio_data.max()), (-HEIGHT//4, HEIGHT//4))
        audio_data = (previous_audio_data + current_audio_data) / 2  # Smooth the transition of audio data
        previous_audio_data = current_audio_data  # Update previous audio data
        volume = np.linalg.norm(audio_data)  # Calculate the volume of the current audio data
        if volume > THRESHOLD:  # Check if the volume exceeds the threshold to start raining
            raining = True
            if not is_recording:  # Start recording if not already recording
                is_recording = True
                recorded_frames = []  # Reset recorded frames list
        else:
            raining = False
            audio_data = np.array([0]*WIDTH)
            if is_recording:
                is_recording = False  
                recording_duration = time.time() - recording_start_time
                if recording_duration >= 0.2:
                    save_recording(recorded_frames,p)
        if is_recording:
            recorded_frames.append(in_data)  # Append current audio data to recorded frames
        return (in_data, pyaudio.paContinue)  # Continue recording

    p, stream = get_audio_input_stream(audio_callback)  # Get the audio input stream and start it
    stream.start_stream()  # Start the audio stream

    running = True
    while running:  # Main loop
        for event in pygame.event.get():  # Event handling
            if event.type == pygame.QUIT:  # Check for window close button
                running = False  # Stop the loop

        screen.fill(BLACK)  # Fill the screen with black

        for col in columns:  # Update and draw each column
            col.update(raining, split_screen)
            col.draw(screen, split_screen)

        draw_waveform(screen, audio_data, raining, split_screen)  # Draw the audio waveform

        pygame.display.flip()  # Update the full display surface to the screen
        clock.tick(20)  # Maintain program speed by limiting frames per second

    stream.stop_stream()  # Stop the audio stream
    stream.close()  # Close the audio stream
    p.terminate()  # Terminate the PyAudio session
    pygame.quit()  # Uninitialize all pygame modules


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

if __name__ == "__main__":
    main()