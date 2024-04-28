import pygame
from settings import WIDTH, HEIGHT
from drawing import draw_button

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
    pygame.event.clear()  # Clear the event queue to avoid carrying over previous events
    encryption_options = ["128bit", "256bit", "512bit", "1024bit"]
    selected_option = None
    # Wait for all mouse buttons to be released
    while any(pygame.mouse.get_pressed()):
        pygame.event.pump()  # Process event queue

    mouse_was_pressed = False  # Track if the mouse was previously pressed

    while selected_option is None:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill((0, 0, 0))
        for i, option in enumerate(encryption_options):
            if draw_button(screen, option + " CyberKeys Encryption", (WIDTH / 2 - 100, 100 + i * 60), (200, 50), (70, 130, 180), mouse_pos):
                if pygame.mouse.get_pressed()[0] and not mouse_was_pressed:
                    selected_option = option
                    break
        mouse_was_pressed = pygame.mouse.get_pressed()[0]  # Update the state of the mouse
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    limit = get_user_input(screen, "Enter limit quantity (0 for no limit): ")
    return selected_option, limit


def get_user_input(screen, prompt):
    user_input = ''
    base_font = pygame.font.Font(None, 32)
    input_rect = pygame.Rect(WIDTH / 2 - 100, HEIGHT / 2, 140, 32)
    prompt_rect = pygame.Rect(WIDTH / 2 - 100, HEIGHT / 2 - 40, 200, 32)
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
        prompt_surface = base_font.render(prompt, True, (255, 255, 255))
        screen.blit(prompt_surface, (prompt_rect.x + 5, prompt_rect.y + 5))
        text_surface = base_font.render(user_input, True, (255, 255, 255))
        screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        pygame.draw.rect(screen, color, input_rect, 2)
        pygame.display.flip()
