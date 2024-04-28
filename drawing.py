import pygame
from settings import WIDTH, HEIGHT, NEON_BLUE, WHITE,rainbow_colors



def interpolate_color(ratio, color_palette):
    """ Interpolates a color within a palette based on the ratio (0 to 1). """
    max_index = len(color_palette) - 1
    # Multiply ratio by the number of transitions between colors
    scaled_ratio = ratio * max_index
    first_index = int(scaled_ratio)
    second_index = min(first_index + 1, max_index)
    interpolation = scaled_ratio - first_index
    # Interpolate between the two closest colors
    start_color = color_palette[first_index]
    end_color = color_palette[second_index]
    # Linear interpolation of each color channel
    return tuple([
        int(start_color[i] + (end_color[i] - start_color[i]) * interpolation)
        for i in range(3)
    ])



def draw_waveform(screen, audio_data, raining, split_screen):
    if split_screen:
        screen = pygame.Surface((WIDTH // 2, HEIGHT))

    num_circles = 50
    step_size = (WIDTH // 2 if split_screen else WIDTH) // num_circles + 2
    radius = step_size // 2 - 2

    if raining:
        for i in range(num_circles):
            color = interpolate_color(i / num_circles, rainbow_colors)
            height = min(abs(audio_data[i * (len(audio_data) // num_circles)]) * 2.5 * 0.5, HEIGHT)
            y = max(0, HEIGHT // 2 - height // 2)
            pygame.draw.ellipse(screen, color, (i * step_size + 2, y, radius * 2, height))

def draw_button(screen, text, position, size, color, mouse_pos):
    pygame.draw.rect(screen, color, (*position, *size))  # Draw the button rectangle
    font = pygame.font.Font(None, 30)  # Use default font with size 30
    text_surf = font.render(text, True, (255, 255, 255))  # Render the text
    text_rect = text_surf.get_rect(center=(position[0] + size[0] / 2, position[1] + size[1] / 2))  # Center the text
    screen.blit(text_surf, text_rect)  # Blit the text to the screen
    return position[0] <= mouse_pos[0] <= position[0] + size[0] and position[1] <= mouse_pos[1] <= position[1] + size[1]  # Return if mouse is over the button
