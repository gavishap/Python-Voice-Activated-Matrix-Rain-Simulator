import pygame
from settings import WIDTH, HEIGHT
from drawing import draw_button

def main_menu(screen):
    running = True
    background_image = pygame.image.load('Blurry_circle.PNG')
    button_color = (10, 24, 74)  # Dark blue color
    glow_effect = (255, 255, 255)  # White glow effect
    last_click_time = None
    double_click_threshold = 500  # milliseconds

    while running:
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(background_image, (0, 0))
        if draw_button(screen, "Simple Mode", (WIDTH / 2 - 150, HEIGHT / 2 - 90), (300, 100), button_color, mouse_pos, border_radius=15, shadow_color=glow_effect):
            if pygame.mouse.get_pressed()[0]:
                return "simple"
        if draw_button(screen, "CyberBit Mode", (WIDTH / 2 - 150, HEIGHT / 2 + 20), (300, 100), button_color, mouse_pos, border_radius=15, shadow_color=glow_effect):
            if pygame.mouse.get_pressed()[0]:
                return "cyberbit"
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if last_click_time and pygame.time.get_ticks() - last_click_time < double_click_threshold:
                    running = False
                    pygame.quit()
                    exit()
                last_click_time = pygame.time.get_ticks()

def cyberbit_mode_config(screen):
    pygame.event.clear()  # Clear the event queue to avoid carrying over previous events
    encryption_options = ["128bit", "256bit", "512bit", "1024bit"]
    selected_option = None
    background_image = pygame.image.load('Blurry_circle.PNG')
    button_color = (10, 24, 74)  # Dark blue color
    glow_effect = (255, 255, 255)  # White glow effect
    last_click_time = None
    double_click_threshold = 500  # milliseconds
    # Wait for all mouse buttons to be released
    while any(pygame.mouse.get_pressed()):
        pygame.event.pump()  # Process event queue

    mouse_was_pressed = False  # Track if the mouse was previously pressed

    while selected_option is None:
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(background_image, (0, 0))
        total_buttons_height = len(encryption_options) * 100 + (len(encryption_options) - 1) * 20
        start_y = (HEIGHT - total_buttons_height) / 2
        for i, option in enumerate(encryption_options):
            button_y = start_y + i * (100 + 20)  # 100 is button height, 20 is space between buttons
            if draw_button(screen, option + " CyberKeys Encryption", (WIDTH / 2 - 150, button_y), (300, 100), button_color, mouse_pos, border_radius=15, shadow_color=glow_effect):
                if pygame.mouse.get_pressed()[0] and not mouse_was_pressed:
                    selected_option = option
                    break
        mouse_was_pressed = pygame.mouse.get_pressed()[0]  # Update the state of the mouse
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if last_click_time and pygame.time.get_ticks() - last_click_time < double_click_threshold:
                    pygame.quit()
                    exit()
                last_click_time = pygame.time.get_ticks()

    limit = get_user_input(screen, "Enter limit quantity (0 for no limit): ")
    return selected_option, limit


def get_user_input(screen, prompt):
    user_input = ''
    base_font = pygame.font.Font(None, 32)
    input_rect = pygame.Rect(WIDTH / 2 - 150, HEIGHT / 2, 300, 100)
    prompt_rect = pygame.Rect(WIDTH / 2 - 150, HEIGHT / 2 - 120, 300, 32)
    color_active = pygame.Color('lightskyblue3')
    color_passive = pygame.Color('gray15')
    color = color_passive
    active = False
    background_image = pygame.image.load('Blurry_circle.PNG')
    last_click_time = None
    double_click_threshold = 500  # milliseconds
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
                if last_click_time and pygame.time.get_ticks() - last_click_time < double_click_threshold:
                    pygame.quit()
                    exit()
                last_click_time = pygame.time.get_ticks()
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return user_input
                    elif event.key == pygame.K_BACKSPACE:
                        user_input = user_input[:-1]
                    else:
                        user_input += event.unicode

        screen.blit(background_image, (0, 0))
        prompt_surface = base_font.render(prompt, True, (255, 255, 255))
        screen.blit(prompt_surface, (prompt_rect.x + 5, prompt_rect.y + 5))
        text_surface = base_font.render(user_input, True, (255, 255, 255))
        screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        pygame.draw.rect(screen, color, input_rect, 2, border_radius=15)
        pygame.display.flip()
