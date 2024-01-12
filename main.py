import pygame
import random

# Константы
WINDOW_WIDTH = 1408
WINDOW_HEIGHT = 720
GAME_ZONE = screen = pygame.display.set_mode((1024, 720))
PLATFORM_WIDTH = 160
PLATFORM_HEIGHT = 20
BALL_RADIUS = 10
BLOCK_WIDTH = 64
BLOCK_HEIGHT = 33
BLOCKS_PER_ROW = (WINDOW_WIDTH // BLOCK_WIDTH) - 6

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
        self.image = pygame.image.load('data/platform_AKTIVE.png')  # загрузка картинки "block.png"
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
        if self.rect.right > 1024:
            self.rect.right = 1024


# Класс для шарика
class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([BALL_RADIUS * 2, BALL_RADIUS * 2])
        self.image = pygame.image.load('data/ball.png')  # загрузка картинки "block.png"
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
        if self.rect.x <= 0 or self.rect.right >= 1024:
            self.speed_x = -self.speed_x
        if self.rect.y <= 0:
            self.speed_y = -self.speed_y

        # Отскок шарика от платформы
        if pygame.sprite.collide_rect(self, platform):
            self.speed_y = -self.speed_y


# Класс для блоков
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, asset):
        super().__init__()
        self.image = pygame.image.load(asset)  # загрузка картинки "block.png"
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# Инициализация Pygame
pygame.init()

# Создание окна игры
window = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])
pygame.display.set_caption("Арканоид")

background_image = pygame.image.load("data/background.png")
background_surface = pygame.Surface((1024, 720))
background_image = pygame.transform.scale(background_image, (1024, 720))
background_surface.blit(background_image, (0, 0))

pygame.draw.rect(window, WHITE,
                 (1024, 0, WINDOW_WIDTH, WINDOW_WIDTH), 0)

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
for row in range(10):
    for col in range(BLOCKS_PER_ROW):
        block = Block(col * BLOCK_WIDTH, row * BLOCK_HEIGHT,
                      random.choice(['data/block.png', 'data/block_RED.png', 'data/block_WHITE.png']))
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
    GAME_ZONE.blit(background_surface, (0, 0))
    all_sprites.draw(GAME_ZONE)

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
