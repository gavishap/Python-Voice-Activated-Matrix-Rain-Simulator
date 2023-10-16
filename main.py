import pygame
import random
import pyaudio
import numpy as np
import wave
import time
import datetime
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
    # else:
    #    pygame.draw.line(screen, WHITE, (0, HEIGHT//2), (WIDTH // 2 if split_screen else WIDTH, HEIGHT//2), 2)  # Draw a pink line
# class Button:
#     def __init__(self, x, y, w, h, text):
#         self.rect = pygame.Rect(x, y, w, h)
#         self.text = text

#     def draw(self, screen, split_screen):
#         if split_screen:
#             # Adjust the position of the button for split screen
#             rect = pygame.Rect(self.rect.x // 2, self.rect.y, self.rect.w // 2, self.rect.h)
#         else:
#             rect = self.rect

#         pygame.draw.rect(screen, WHITE, rect, 2)
#         label = FONT.render(self.text, 1, WHITE)
#         screen.blit(label, (rect.x + 10, rect.y + 10))

#     def clicked(self, pos):
#         return self.rect.collidepoint(pos)
recording_counter = 0
background_noise = None
background_noise_duration = 5 
def main():
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Matrix Rain with Voice Waveform and Audio Recording')
    clock = pygame.time.Clock()
    audio_buffer = b''  # An empty byte string

    columns = [Column(x, random.randint(-HEIGHT, -FONT_SIZE)) for x in range(0, WIDTH, 15)]
    raining = False
    audio_data = np.array([0]*WIDTH)  # Initialize with zeros
    previous_audio_data = np.array([0]*1024)  # Initialize with zeros
    

    # start_recording_btn = Button(10, HEIGHT - 40, 120, 30, "Start Recording")
    # custom_timer_btn = Button(140, HEIGHT - 40, 200, 30, "Custom Timer")
    split_screen = False
    # split_screen_btn = Button(350, HEIGHT - 40, 200, 30, "Split Screen")
    is_recording = False
    recorded_frames = []
    start_time = None
    custom_duration = None
    global recording_counter
    # Add these variables before the main loop
    is_recording = False
    recorded_frames = []
    recording_start_time = None
    filename_prefix = "recording_"
    
    

    def audio_callback(in_data, frame_count, time_info, status):
        global recording_counter  # Declare recording_counter as global
        nonlocal raining, audio_data, audio_buffer, previous_audio_data, is_recording, recorded_frames, recording_start_time
        audio_buffer = in_data  # Storing the raw audio data for later usage
        current_audio_data = np.frombuffer(in_data, dtype=np.int16)
        current_audio_data = np.interp(current_audio_data, (current_audio_data.min(), current_audio_data.max()), (-HEIGHT//4, HEIGHT//4))
        audio_data = (previous_audio_data + current_audio_data) / 2  # Average current and previous frame's audio data
        previous_audio_data = current_audio_data  # Store current frame's audio data for next frame
        volume = np.linalg.norm(audio_data)
        if volume > THRESHOLD:
            raining = True
            if not is_recording:  # Start recording if not already recording
                is_recording = True
                recorded_frames = []  # Clear previous frames
                recording_start_time = time.time()  # Add this line
        else:
            raining = False
            audio_data = np.array([0]*WIDTH)  # Reset to flatline when quiet
            if is_recording:  # Stop recording if currently recording
                is_recording = False
                recording_duration = time.time() - recording_start_time  # Calculate recording duration
                if recording_duration >= 0.2:  # Only save if recording is at least 0.06 seconds long
                    # Get current time
                    now = datetime.datetime.now()
                    timestamp = now.strftime("%H_%M_%S") + "_" + now.strftime("%f")[:3]
                    # Save recording to a file
                    # filename = timestamp + ".wav"
                    # with wave.open(filename, 'wb') as wf:
                    #     wf.setnchannels(1)
                    #     wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                    #     wf.setframerate(44100)
                    #     wf.writeframes(b''.join(recorded_frames))
                    # Save binary data to a file
                    binary_filename = "recordings/" + timestamp + ".ky"
                    with open(binary_filename, 'w') as bf:  # Open file in text mode
                        for frame in recorded_frames:
                            binary_string = ''.join(f'{byte:08b}' for byte in frame)  # Convert byte string to binary string
                            bf.write(binary_string)
                    # Convert binary data back to wav file
                    converted_filename = "recordings/" + timestamp + "_converted.wav"
                    with open(binary_filename, 'r') as bf, wave.open(converted_filename, 'wb') as wf:
                        binary_string = bf.read()
                        byte_string = bytes(int(binary_string[i:i+8], 2) for i in range(0, len(binary_string), 8))
                        wf.setnchannels(1)
                        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                        wf.setframerate(44100)
                        wf.writeframes(byte_string)
                    recording_counter += 1
        if is_recording:
            recorded_frames.append(in_data)
        return (in_data, pyaudio.paContinue)


    p, stream = get_audio_input_stream(audio_callback)
    stream.start_stream()
    
    running = True
    while running:
       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # if start_recording_btn.clicked(pos):
                #     if is_recording:  # Stop recording
                #         is_recording = False
                #         filename = input("Enter a name for the recording: ") + ".wav"
                #         with wave.open(filename, 'wb') as wf:
                #             wf.setnchannels(1)
                #             wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                #             wf.setframerate(44100)
                #             wf.writeframes(b''.join(recorded_frames))
                #         recorded_frames.clear()
                #         start_recording_btn.text = "Start Recording"
                #     else:  # Start recording
                #         is_recording = True
                #         start_recording_btn.text = "Stop Recording"
                # elif custom_timer_btn.clicked(pos):
                #     mins = float(input("Enter duration in minutes: "))
                #     custom_duration = mins * 60  # Convert to seconds
                #     start_time = pygame.time.get_ticks()
                #     is_recording = True
                # elif split_screen_btn.clicked(pos):
                #     split_screen = not split_screen  # Toggle split_screen
        if is_recording:
            if audio_buffer:
                recorded_frames.append(audio_buffer)
        screen.fill(BLACK)
        
        for col in columns:
            col.update(raining, split_screen)
            col.draw(screen, split_screen)

        draw_waveform(screen, audio_data, raining,split_screen)

        if is_recording and raining:
            if audio_buffer:
                recorded_frames.append(audio_buffer)


        if custom_duration and (pygame.time.get_ticks() - start_time) / 1000 > custom_duration:
            custom_duration = None
            start_time = None
            is_recording = False
            filename = input("Enter a name for the recording: ") + ".wav"
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b''.join(recorded_frames))
            recorded_frames.clear()
        #     start_recording_btn.text = "Start Recording"

        # start_recording_btn.draw(screen, split_screen)
        # custom_timer_btn.draw(screen, split_screen)
        # split_screen_btn.draw(screen, split_screen)  # Add this line
        pygame.display.flip()
        clock.tick(20)

    stream.stop_stream()
    stream.close()
    p.terminate()
    pygame.quit()

if __name__ == "__main__":
    main()
