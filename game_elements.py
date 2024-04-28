import pygame
import random
from settings import WIDTH, HEIGHT, DARK_BLUE, WHITE

class Column:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = random.uniform(1, 10)  # Random initial speed
        self.speed_increase = 0.2  # Incremental speed increase
        self.initial_font_size = random.randint(17, 20)
        self.font_size = self.initial_font_size
        self.should_grow = random.choice([True, False])
        self.font = pygame.font.Font('DISPLAY FREE TFB.ttf', self.font_size)
        self.symbols = [random.choice(["0", "1"]) for _ in range(random.randint(4, 10))]
        self.growth_timer = pygame.time.get_ticks()

    def draw(self, screen, split_screen):
        for i, s in enumerate(self.symbols):
            color = WHITE if random.random() < 0.2 else DARK_BLUE
            label = self.font.render(s, 1, color)
            label_surface = pygame.Surface(label.get_size(), pygame.SRCALPHA)
            alpha = max(255 - int((self.y / HEIGHT) * 255 * 1.5), 0)
            label_surface.set_alpha(alpha)
            label_surface.blit(label, (0, 0))
            
            if split_screen:
                screen.blit(label_surface, (self.x + WIDTH // 2, self.y + i * self.font_size * 0.7))
            else:
                screen.blit(label_surface, (self.x, self.y + i * self.font_size * 0.7))

    def update(self, raining, split_screen):
        self.y += self.speed
        self.speed += self.speed_increase
        
        if self.y - len(self.symbols) * self.font_size > HEIGHT and raining:
            if split_screen:
                self.x = random.randint(WIDTH // 2, WIDTH)
            else:
                self.x = random.randint(0, WIDTH)
            self.y = random.randint(-HEIGHT, -self.font_size)
            self.symbols = [random.choice(["0", "1"]) for _ in range(random.randint(4, 10))]
            self.font_size = self.initial_font_size
            self.font = pygame.font.Font('DISPLAY FREE TFB.ttf', self.font_size)
            self.speed = random.uniform(1, 10)
        if self.should_grow:
            if pygame.time.get_ticks() - self.growth_timer > 40 and self.font_size < 40:
                self.font_size += 1
                self.font = pygame.font.Font('DISPLAY FREE TFB.ttf', self.font_size)
                self.growth_timer = pygame.time.get_ticks()
