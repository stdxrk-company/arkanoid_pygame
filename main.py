import pygame

import settings as cfg
from game import audio
from screens.game_screen import run as game_screen
from screens.menu_screen import run as menu_screen


def main():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
    pygame.display.set_caption("Arkanoid")
    clock = pygame.time.Clock()
    audio.init()
    audio.play_music()

    # Menu -> game -> back to menu, until the player quits
    while menu_screen(screen, clock):
        if not game_screen(screen, clock, level=1):
            break

    pygame.quit()


if __name__ == "__main__":
    main()
