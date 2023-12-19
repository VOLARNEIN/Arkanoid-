import pygame
import random

# Константы
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 20
BALL_RADIUS = 10
BLOCK_WIDTH = (WINDOW_WIDTH - 10) // 10
BLOCK_HEIGHT = 20
BLOCKS_PER_ROW = WINDOW_WIDTH // BLOCK_WIDTH

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Класс для платформы
class Platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([PLATFORM_WIDTH, PLATFORM_HEIGHT])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = (WINDOW_WIDTH - PLATFORM_WIDTH) // 2
        self.rect.y = WINDOW_HEIGHT - PLATFORM_HEIGHT

    def update(self):
        # Перемещение платформы вместе с курсором мыши
        pos = pygame.mouse.get_pos()
        self.rect.x = pos[0] - PLATFORM_WIDTH / 2

        # Ограничение платформы в пределах окна
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH

# Класс для шарика
class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([BALL_RADIUS * 2, BALL_RADIUS * 2])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = WINDOW_WIDTH // 2
        self.rect.y = WINDOW_HEIGHT // 2
        self.speed_x = random.choice([-2, 2])
        self.speed_y = -2

    def update(self):
        # Обновление позиции шарика
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Отскок шарика от стен
        if self.rect.x <= 0 or self.rect.right >= WINDOW_WIDTH:
            self.speed_x = -self.speed_x
        if self.rect.y <= 0:
            self.speed_y = -self.speed_y

        # Отскок шарика от платформы
        if pygame.sprite.collide_rect(self, platform):
            self.speed_y = -self.speed_y

# Класс для блоков
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([BLOCK_WIDTH, BLOCK_HEIGHT])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Инициализация Pygame
pygame.init()

# Создание окна игры
window = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])
pygame.display.set_caption("Арканоид")

# Создание спрайтов
all_sprites = pygame.sprite.Group()
blocks = pygame.sprite.Group()

# Создание платформы
platform = Platform()
all_sprites.add(platform)

# Создание шарика
ball = Ball()
all_sprites.add(ball)

# Создание блоков
for row in range(5):
    for col in range(BLOCKS_PER_ROW):
        block = Block(col * BLOCK_WIDTH, row * BLOCK_HEIGHT)
        all_sprites.add(block)
        blocks.add(block)

# Главный цикл игры
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Обновление спрайтов
    all_sprites.update()

    # Отрисовка игровых объектов
    window.fill(BLACK)
    all_sprites.draw(window)

    # Проверка столкновения шарика с блоками
    collisions = pygame.sprite.spritecollide(ball, blocks, True)
    if collisions:
        ball.speed_y = -ball.speed_y

    # Проверка окончания игры
    if ball.rect.y >= WINDOW_HEIGHT:
        running = False

    # Обновление экрана
    pygame.display.flip()

    # Ограничение частоты обновления экрана
    clock.tick(60)

# Завершение игры
pygame.quit()