import pygame
import random
import sqlite3
import pygame.mixer
import os

from pygame.locals import *

os.environ["SDL_VIDEO_CENTERED"] = "1"

# Константы
WINDOW_WIDTH = 1408
WINDOW_HEIGHT = 720
GAME_ZONE = screen = pygame.display.set_mode((1024, 720))
PLATFORM_WIDTH = 160
PLATFORM_HEIGHT = 20
BALL_RADIUS = 10
BLOCK_WIDTH = 64
BLOCK_HEIGHT = 32
BLOCKS_PER_ROW = (WINDOW_WIDTH // BLOCK_WIDTH) - 6
max_speed = 8
seconds = 0
mseconds = 0
ENERGY_MAX = 100
ENERGY_DECREASE_RATE = 1 / 60  # тк в 1 секунде 60 кадров

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)


# Класс для платформы
class Platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([PLATFORM_WIDTH, PLATFORM_HEIGHT])
        self.rect = self.image.get_rect()
        self.rect.x = (WINDOW_WIDTH - PLATFORM_WIDTH) // 2
        self.rect.y = WINDOW_HEIGHT - PLATFORM_HEIGHT

    def update(self):
        global energy
        # Перемещение платформы вместе с курсором мыши
        if energy != 0:
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
        self.image = pygame.image.load('data/asset/ball.png')  # загрузка картинки "block_GREEN.png"
        self.rect = self.image.get_rect()
        self.rect.x = 1024 // 2
        self.rect.y = WINDOW_HEIGHT // 2
        self.speed_x = random.choice([-1.5, 1.5])
        self.speed_y = 1.5

        self.time_count = 0
        self.speed_increase = 0.5

    def update(self):
        # Обновление позиции шарика
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Проверка столкновений с краями окна и их обработка
        if self.rect.left <= 0:
            self.rect.left = 0
            self.speed_x *= -1
            sound_punch.play()
        elif self.rect.right >= 1024:
            self.rect.right = 1024
            self.speed_x *= -1
            sound_punch.play()
        if self.rect.top <= 0:
            self.rect.top = 0
            self.speed_y *= -1
            sound_punch.play()

        # Отскок шарика от платформы
        if pygame.sprite.collide_rect(self, platform):
            if self.speed_y > 0:  # проверка направления движения шарика, чтобы избежать проваливания через платформу
                self.speed_y = -self.speed_y
                sound_punch.play()

        # Увеличение скорости каждые 30 секунд
        self.time_count += 1
        if self.time_count == 1800 and (
                self.speed_x != max_speed or self.speed_x != -max_speed):  # 1800 кадров = 30 секунды (если кадры обновляются с частотой 60 кадров в секунду)
            if self.speed_x > 0:
                self.speed_x += self.speed_increase
            else:
                self.speed_x -= self.speed_increase
            if self.speed_y > 0:
                self.speed_y += self.speed_increase
            else:
                self.speed_y -= self.speed_increase

            self.time_count = 0


# Классы для блоков
class Block_WHITE(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('data/asset/block_WHITE.png')  # загрузка картинки "block_GREEN.png"
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Block_RED(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('data/asset/block_RED.png')  # загрузка картинки "block_GREEN.png"
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Block_GREEN(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('data/asset/block_GREEN.png')  # загрузка картинки "block_GREEN.png"
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Block_BLUE(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('data/asset/block_BLUE.png')  # загрузка картинки "block_GREEN.png"
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Block_YELLO(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('data/asset/block_YELLOW.png')  # загрузка картинки "block_GREEN.png"
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# Инициализация Pygame
pygame.init()

# Фоновая музыка
pygame.mixer.music.load('data/music/background_game_music.mp3')
pygame.mixer.music.play(10)
pygame.mixer.music.set_volume(0.5)

# Звуки
sound_punch = pygame.mixer.Sound('data/sound/punch.mp3')
sound_hit = pygame.mixer.Sound('data/sound/hit.mp3')
sound_good = pygame.mixer.Sound('data/sound/good.mp3')
sound_fail = pygame.mixer.Sound('data/sound/fail.mp3')

# Создание окна игры
window = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])
pygame.display.set_caption("Arkanoid+")

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
        block = random.randrange(0, 23)
        if 0 <= block <= 10:
            block = Block_WHITE(col * BLOCK_WIDTH, row * BLOCK_HEIGHT)
        elif 10 < block <= 17:
            block = Block_RED(col * BLOCK_WIDTH, row * BLOCK_HEIGHT)
        elif 17 < block <= 20:
            block = Block_GREEN(col * BLOCK_WIDTH, row * BLOCK_HEIGHT)
        elif block == 21:
            block = Block_BLUE(col * BLOCK_WIDTH, row * BLOCK_HEIGHT)
        elif block == 22:
            block = Block_YELLO(col * BLOCK_WIDTH, row * BLOCK_HEIGHT)
        all_sprites.add(block)
        blocks.add(block)

# Создание фона
background_image = pygame.image.load("data/asset/background.png")
background_image = pygame.transform.scale(background_image, (1024, 720))
GAME_ZONE.blit(background_image, (0, 0))

pygame.draw.rect(window, WHITE,
                 (1024, 0, WINDOW_WIDTH, WINDOW_WIDTH), 0)
font = pygame.font.Font(None, 45)

# Позиция и размеры шкалы энергии
sx = 1034
sy = 600
swidth = 364
sheight = 50
pygame.draw.rect(screen, BLACK, (sx - 2, sy - 2, swidth + 4, sheight + 4))

# Размер прогресс-бара (изначально заполненного)
progress_width = swidth
energy = ENERGY_MAX

# Подключение к базе данных
conn = sqlite3.connect("victorina.db")
cursor = conn.cursor()


# Функция для отображения вопроса и вариантов ответов
def display_question(question_line1, question_line2, options):
    pygame.draw.rect(window, WHITE, (1034, 0, WINDOW_WIDTH, 350), 0)
    font = pygame.font.Font(None, 30)
    question_text1 = font.render(question_line1, True, BLACK)
    question_text2 = font.render(question_line2, True, BLACK)
    screen.blit(question_text1, (1034, 60))
    screen.blit(question_text2, (1034, 77))

    option_y = 140
    for i, option in enumerate(options):
        option_text = font.render(f"{str(i + 1)}) {option}", True, BLACK)
        screen.blit(option_text, (1034, option_y))
        option_y += 50


# Функция для получения случайного вопроса из базы данных
def get_random_question():
    random_number = random.randint(1, 40)
    cursor.execute("SELECT * FROM average WHERE number=?", (random_number,))
    question_row = cursor.fetchone()
    if len(question_row[1]) >= 30:
        question_line1, question_line2 = split_text(question_row[1])
    else:
        question_line1, question_line2 = question_row[1], ''
    options = question_row[2:6]
    answer = question_row[6]
    return question_line1, question_line2, options, answer


# Деление вопроса на строки
def split_text(text):
    # разбиваем текст на слова
    words = text.split()
    line1 = ' '.join(words[:len(words) // 2])
    line2 = ' '.join(words[len(words) // 2:])

    return line1.strip(), line2.strip()


score = 0
question_line1, question_line2, options, answer = get_random_question()
display_question(question_line1, question_line2, options)

# Скрывать курсор мыши
pygame.mouse.set_visible(False)

# Главный цикл игры
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.mouse.set_visible(True)
            running = False
            import main

        if event.type == KEYDOWN and K_1 <= event.key <= K_4:
            selected_option = int(event.unicode)
            if selected_option == int(answer):
                score += 1
                energy += 5
                question_line1, question_line2, options, answer = get_random_question()
                display_question(question_line1, question_line2, options)
                sound_good.play()
            else:
                score -= 1
                energy -= 5
                question_line1, question_line2, options, answer = get_random_question()
                display_question(question_line1, question_line2, options)
                sound_fail.play()

        if event.type == KEYDOWN and event.key == K_ESCAPE:
            pygame.mouse.set_visible(True)
            running = False
            import main

    # Обновление спрайтов
    all_sprites.update()

    # Обновление таймера
    time_surface = font.render(f"{seconds:02}:{mseconds:02}", True, BLACK)

    # Уменьшение energy
    energy -= ENERGY_DECREASE_RATE
    if energy < 0:
        energy = 0
    if energy > 100:
        energy = 100

    if energy != 0:
        platform.image = pygame.image.load('data/asset/platform_AKTIVE.png')  # загрузка картинки "block_GREEN.png"
    else:
        platform.image = pygame.image.load('data/asset/platform_NONAKTIVE.png')

    # Отрисовка шкалы
    pygame.draw.rect(screen, RED, (sx, sy, swidth, sheight))
    pygame.draw.rect(screen, GREEN, (sx, sy, progress_width, sheight))

    # Изменение размеров прогресс-бара
    progress_width = int((energy / ENERGY_MAX) * swidth)

    # Отрисовка игровых объектов
    GAME_ZONE.blit(background_image, (0, 0))
    all_sprites.draw(GAME_ZONE)
    pygame.draw.rect(window, WHITE, (1034, 0, WINDOW_WIDTH, 60), 0)
    window.blit(time_surface, (1226 - time_surface.get_width() // 2, 40 - time_surface.get_height() // 2))

    # Увеличение секунд и минут таймера
    mseconds += 1
    if mseconds == 60:
        mseconds = 0
        seconds += 1

    # Проверка столкновения шарика с блоками
    collisions = pygame.sprite.spritecollide(ball, blocks, True)
    if collisions:
        for block_class in collisions:
            if 'Block_WHITE' in str(block_class):
                pass
        ball.speed_y = -ball.speed_y
        sound_hit.play()

    # Проверка окончания игры
    if ball.rect.y >= WINDOW_HEIGHT:
        pygame.mouse.set_visible(True)
        running = False
        import main

    # Обновление экрана
    pygame.display.update()

    # Ограничение частоты обновления экрана
    clock.tick(60)

# Завершение игры
pygame.quit()
