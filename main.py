import pygame

# Инициализация Pygame
pygame.init()

# Определение цветов
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Определение размеров окна
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Создание окна игры
size = (WINDOW_WIDTH, WINDOW_HEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Arkanoid")

# Определение переменных
ball_radius = 10
paddle_width = 100
paddle_height = 10
paddle_x = (WINDOW_WIDTH - paddle_width) // 2
paddle_y = WINDOW_HEIGHT - paddle_height - 10
paddle_speed = 5
ball_x = WINDOW_WIDTH // 2
ball_y = WINDOW_HEIGHT // 2
ball_dx = 3
ball_dy = -3
block_width = 60
block_height = 20
block_gap = 5
block_rows = 5
block_cols = WINDOW_WIDTH // (block_width + block_gap)
blocks = []

# Создание блоков
for row in range(block_rows):
    for col in range(block_cols):
        x = (block_width + block_gap) * col
        y = (block_height + block_gap) * row
        blocks.append(pygame.Rect(x, y, block_width, block_height))

# Цикл игры
done = False
clock = pygame.time.Clock()
score = 0

while not done:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # Обработка движения мыши
    mouse_x, _ = pygame.mouse.get_pos()
    paddle_x = mouse_x

    # Движение шарика
    ball_x += ball_dx
    ball_y += ball_dy

    # Обработка столкновения с границами окна
    if ball_x < ball_radius or ball_x > WINDOW_WIDTH - ball_radius:
        ball_dx *= -1
    if ball_y < ball_radius:
        ball_dy *= -1
    if ball_y > WINDOW_HEIGHT - ball_radius:
        done = True  # Игра окончена, если шарик упал за нижнюю границу

    # Обработка столкновения с платформой
    if ball_y > paddle_y - ball_radius and paddle_x - ball_radius < ball_x < paddle_x + paddle_width + ball_radius:
        ball_dy *= -1

    # Обработка столкновений со значениями блоков
    for block in blocks:
        if block.collidepoint(ball_x, ball_y):
            blocks.remove(block)
            ball_dy *= -1
            score += 1

    # Заливка фона
    screen.fill(BLACK)

    # Отрисовка объектов
    pygame.draw.circle(screen, RED, (ball_x, ball_y), ball_radius)
    pygame.draw.rect(screen, GREEN, (paddle_x, paddle_y, paddle_width, paddle_height))

    for block in blocks:
        pygame.draw.rect(screen, BLUE, block)

    # Обновление экрана
    pygame.display.flip()

    # Ограничение количества кадров
    clock.tick(60)

# Завершение игры
pygame.quit()