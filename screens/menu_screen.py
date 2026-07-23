"""screens/menu_screen.py – start menu with the bonus legend."""

import pygame

import settings as cfg
from game import audio
from game.entities import Bonus

BONUS_DESCRIPTIONS = {
    "extend": "Wider paddle",
    "multiball": "Two extra balls",
    "laser": "Laser paddle (SPACE to shoot)",
    "extra_life": "Extra life",
    "shrink": "Narrower paddle",
    "speed_up": "Faster balls",
    "speed_down": "Slower balls",
}


def run(screen: pygame.Surface, clock: pygame.time.Clock) -> bool:
    """ Shows the start menu. Returns True to start the game, False to quit. """
    title_font = pygame.font.Font(None, 96)
    text_font = pygame.font.Font(None, 32)
    small_font = pygame.font.Font(None, 24)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    audio.play("bonus")
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False

        screen.fill(cfg.BLACK)

        title = title_font.render("ARKANOID", True, cfg.CYAN)
        screen.blit(title, title.get_rect(center=(cfg.WIDTH // 2, 110)))

        # Bonus legend
        legend_left = cfg.WIDTH // 2 - 160
        header = text_font.render("Bonuses:", True, cfg.WHITE)
        screen.blit(header, (legend_left, 190))
        y = 230
        for bonus_type, props in Bonus.TYPES.items():
            icon = pygame.Rect(legend_left, y, 24, 24)
            pygame.draw.rect(screen, props["color"], icon, border_radius=5)
            letter = small_font.render(props["letter"], True, cfg.BLACK)
            screen.blit(letter, letter.get_rect(center=icon.center))
            line = small_font.render(BONUS_DESCRIPTIONS[bonus_type], True, cfg.GRAY)
            screen.blit(line, (icon.right + 12, y + 4))
            y += 32

        if pygame.time.get_ticks() % 1000 < 600:  # Blinking prompt
            prompt = text_font.render("Press ENTER to start", True, cfg.WHITE)
            screen.blit(prompt, prompt.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT - 90)))
        hint = small_font.render(
            "Arrows: move    SPACE: laser    ESC: menu / quit", True, cfg.GRAY)
        screen.blit(hint, hint.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT - 50)))

        pygame.display.flip()
        clock.tick(cfg.FPS)
