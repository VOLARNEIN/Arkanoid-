import pygame
import random
import sqlite3
import pygame.mixer
import os
import sys

from pygame.locals import *

os.environ["SDL_VIDEO_CENTERED"] = "1"

# Константы
WINDOW_WIDTH = 1408
WINDOW_HEIGHT = 720
GAME_ZONE = screen = pygame.display.set_mode((1024, 720))
PLATFORM_WIDTH = 104
PLATFORM_HEIGHT = 24
BALL_RADIUS = 10
BLOCK_WIDTH = 64
BLOCK_HEIGHT = 32
BLOCKS_PER_ROW = (WINDOW_WIDTH // BLOCK_WIDTH) - 6
max_speed = 11
seconds = 0
mseconds = 0
ENERGY_MAX = 100
ENERGY_DECREASE_RATE = 1 / 60  # тк в 1 секунде 60 кадров
xSpeed = 0

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
        self.image = pygame.image.load('data/asset/ball.png')
        self.rect = self.image.get_rect()
        self.rect.x = 1024 // 2
        self.rect.y = WINDOW_HEIGHT // 2
        self.speed_x = random.choice([-1.5, 1.5])
        self.speed_y = 1.5

        self.time_count = 0
        self.speed_increase = 0.5

    def update(self):
        global xSpeed
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
                xSpeed += 0.25
            else:
                self.speed_x -= self.speed_increase
                xSpeed += 0.25
            if self.speed_y > 0:
                self.speed_y += self.speed_increase
                xSpeed += 0.25
            else:
                self.speed_y -= self.speed_increase
                xSpeed += 0.25

            self.time_count = 0


# Классы для блоков
class Block_WHITE(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('data/asset/block_WHITE.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Block_RED(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('data/asset/block_RED.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Block_GREEN(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('data/asset/block_GREEN.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Block_BLUE(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('data/asset/block_BLUE.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Block_YELLOW(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('data/asset/block_YELLOW.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Block_VIOLET(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('data/asset/block_VIOLET.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("data/asset/particle.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vx = random.choice([-1, 1]) * random.uniform(1, 5)  # Случайная скорость по оси X
        self.vy = random.uniform(-5, -1)  # Случайная скорость по оси Y

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.vy += 0.2  # Гравитация
        if not self.rect.colliderect(0, 0, 1010, 720):
            self.kill()


# Функция для создания частиц при соприкосновении спрайтов
def create_particles(x, y, num_particles=10):
    particles = pygame.sprite.Group()
    for _ in range(num_particles):
        particle = Particle(x, y)
        particles.add(particle)
    return particles


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
        block = random.randrange(0, 30)
        if 0 <= block <= 13:
            block = Block_WHITE(col * BLOCK_WIDTH, row * BLOCK_HEIGHT)
        elif 13 < block <= 20:
            block = Block_RED(col * BLOCK_WIDTH, row * BLOCK_HEIGHT)
        elif 20 < block <= 23:
            block = Block_GREEN(col * BLOCK_WIDTH, row * BLOCK_HEIGHT)
        elif block == 24:
            block = Block_BLUE(col * BLOCK_WIDTH, row * BLOCK_HEIGHT)
        elif block == 25:
            block = Block_YELLOW(col * BLOCK_WIDTH, row * BLOCK_HEIGHT)
        elif 25 < block <= 30:
            block = Block_VIOLET(col * BLOCK_WIDTH, row * BLOCK_HEIGHT)
        all_sprites.add(block)
        blocks.add(block)

# Создание фона
bi = random.choice(["data/asset/background1.png", "data/asset/background2.jpg", "data/asset/background3.png",
                    "data/asset/background4.jpg", "data/asset/background5.jpg", "data/asset/background6.png"])
background_image = pygame.image.load(bi)
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

energy_text = font.render(f"ШКАЛА ЭНЕРГИИ", True, BLACK)
window.blit(energy_text,
            (sx + swidth // 2 - energy_text.get_width() // 2, sy - 50))

# Главный цикл игры
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == KEYDOWN and K_1 <= event.key <= K_4:
            selected_option = int(event.unicode)
            if selected_option == int(answer):
                score += 100
                energy += 5
                question_line1, question_line2, options, answer = get_random_question()
                display_question(question_line1, question_line2, options)
                sound_good.play()
            else:
                score -= 50
                energy -= 3
                question_line1, question_line2, options, answer = get_random_question()
                display_question(question_line1, question_line2, options)
                sound_fail.play()

        if event.type == KEYDOWN and event.key == K_ESCAPE:
            print(f'Ваш результат: {score * xSpeed}')
            running = False

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
        platform.image = pygame.image.load('data/asset/platform_AKTIVE.png')
    else:
        platform.image = pygame.image.load('data/asset/platform_NONAKTIVE.png')

    # Отрисовка шкалы
    pygame.draw.rect(screen, RED, (sx, sy, swidth, sheight))
    pygame.draw.rect(screen, GREEN, (sx, sy, progress_width, sheight))

    # Изменение размеров прогресс-бара
    progress_width = int((energy / ENERGY_MAX) * swidth)
    energy_count = font.render(f"{int(energy)}/100", True, WHITE)
    window.blit(energy_count,
                (sx + swidth // 2 - energy_count.get_width() // 2, sy + sheight // 2 - energy_count.get_height() // 2))

    # Отрисовка игровых объектов
    GAME_ZONE.blit(background_image, (0, 0))
    all_sprites.draw(GAME_ZONE)
    pygame.draw.rect(window, WHITE, (1034, 0, WINDOW_WIDTH, 60), 0)
    window.blit(time_surface, (1226 - time_surface.get_width() // 2, 40 - time_surface.get_height() // 2))

    pygame.draw.rect(window, WHITE, (1034, 355, WINDOW_WIDTH, 150), 0)
    score_count = font.render(f"СЧЁТ:                {score}", True, BLACK)
    window.blit(score_count, (1034, 360))
    xSpeed_count = font.render(f"СКОРОСТЬ:   х{xSpeed}", True, BLACK)
    window.blit(xSpeed_count, (1034, 425))

    # Увеличение секунд и минут таймера
    mseconds += 1
    if mseconds == 60:
        mseconds = 0
        seconds += 1

    # Проверка столкновения шарика с блоками
    collisions = pygame.sprite.spritecollide(ball, blocks, True)
    if collisions:
        particles = create_particles(ball.rect.centerx, ball.rect.centery, num_particles=10)
        all_sprites.add(particles)
        for block_class in collisions:
            if 'Block_WHITE' in str(block_class):
                score += 100
            elif 'Block_RED' in str(block_class):
                score += 200
                energy -= 5
            elif 'Block_GREEN' in str(block_class):
                score += 150
                energy += 10
            elif 'Block_BLUE' in str(block_class):
                score += 200
                if ball.speed_x != max_speed or ball.speed_x != -max_speed:
                    if ball.speed_x > 0:
                        ball.speed_x += ball.speed_increase
                        xSpeed += 0.25
                    else:
                        ball.speed_x -= ball.speed_increase
                        xSpeed += 0.25
                    if ball.speed_y > 0:
                        ball.speed_y += ball.speed_increase
                        xSpeed += 0.25
                    else:
                        ball.speed_y -= ball.speed_increase
                        xSpeed += 0.25
            elif 'Block_YELLOW' in str(block_class):
                score += 250
                energy = ENERGY_MAX
            elif 'Block_VIOLET' in str(block_class):
                score += 150
                question_line1, question_line2, options, answer = get_random_question()
                display_question(question_line1, question_line2, options)
        ball.speed_y = -ball.speed_y
        sound_hit.play()

    # Проверка окончания игры
    if ball.rect.y >= WINDOW_HEIGHT:
        print(f'Ваш результат: {score * xSpeed}')
        running = False

    # Обновление экрана
    pygame.display.update()

    # Ограничение частоты обновления экрана
    clock.tick(60)

window_width = 800
window_height = 600

# Создание окна
window = pygame.display.set_mode((window_width, window_height))

# Шрифт
font = pygame.font.Font(None, 36)

# Основной игровой цикл
clock = pygame.time.Clock()
game_over = False

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                game_over = True
                import main

    window.fill(BLACK)

    # Отрисовка надписи
    text = font.render(f"Вы продержались {seconds:02} секунд",
                       True, WHITE)
    text_rect = text.get_rect(center=(window_width / 2, window_height / 2 - 25))
    text2 = font.render(
        f"Итоговый результат: {int(score * xSpeed * (energy / 100))}",
        True, WHITE)
    text_rect2 = text2.get_rect(center=(window_width / 2, window_height / 2 + 25))
    window.blit(text, text_rect)
    window.blit(text2, text_rect2)

    # Отрисовка кнопки
    button_text = font.render("Вернуться в главное меню", True, WHITE)
    button_rect = button_text.get_rect(center=(window_width / 2, window_height - 50))
    pygame.draw.rect(window, BLUE, button_rect, border_radius=10)
    window.blit(button_text, button_rect)

    pygame.display.flip()

    # Ограничение количества кадров в секунду
    clock.tick(60)

# Завершение игры
pygame.quit()
