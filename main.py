import pygame
import pygame_menu
from pygame_menu import themes
import pygame.mixer
import os

from pygame.locals import *

os.environ["SDL_VIDEO_CENTERED"] = "1"

pygame.init()
surface = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Arkanoid+")

# Фоновая музыка
pygame.mixer.music.load('data/music/background_menu_music.mp3')
pygame.mixer.music.play(10)
pygame.mixer.music.set_volume(0.5)

# Звуки
sound_choice = pygame.mixer.Sound('data/sound/choice.mp3')
sound_pressing = pygame.mixer.Sound('data/sound/pressing.mp3')


def set_difficulty(value, difficulty):
    print(value)
    print(difficulty)


def start_the_game():
    main_menu._open(loading)
    pygame.time.set_timer(update_loading, 7)


def settings():
    main_menu._open(setting)


main_menu = pygame_menu.Menu('Добро пожаловать', 600, 400, theme=themes.THEME_DARK)
main_menu.add.button('Играть', start_the_game)
main_menu.add.button('Настройки', settings)
main_menu.add.button('Выход', pygame_menu.events.EXIT)

setting = pygame_menu.Menu('Настройки', 600, 400, theme=themes.THEME_DARK)

loading = pygame_menu.Menu('Загрузка игры...', 600, 400, theme=themes.THEME_DARK)
loading.add.progress_bar('Загрузка', progressbar_id="1", default=0, width=200, )

arrow = pygame_menu.widgets.LeftArrowSelection(arrow_size=(10, 15))

update_loading = pygame.USEREVENT + 0

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == update_loading:
            progress = loading.get_widget("1")
            progress.set_value(progress.get_value() + 1)
            if progress.get_value() == 100:
                pygame.time.set_timer(update_loading, 0)
                import game
        if event.type == KEYDOWN and (event.key == K_DOWN or event.key == K_UP):
            sound_choice.play()
        if event.type == KEYDOWN and event.key == KSCAN_KP_ENTER:
            sound_pressing.play()
        if event.type == pygame.QUIT:
            exit()

    if main_menu.is_enabled():
        main_menu.update(events)
        main_menu.draw(surface)
        if (main_menu.get_current().get_selected_widget()):
            arrow.draw(surface, main_menu.get_current().get_selected_widget())

    pygame.display.update()
