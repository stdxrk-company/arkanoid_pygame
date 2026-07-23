"""game/audio.py – background music and sound effects from the assets folder."""

import pygame

import settings as cfg

_sounds: dict[str, pygame.mixer.Sound] = {}


def init() -> None:
    """ Loads all sound effects. Call once after pygame.init(). """
    if pygame.mixer.get_init() is None:  # No audio device - play() becomes a no-op
        return
    for name in ("hit", "bonus", "laser"):
        path = cfg.ASSETS_DIR / f"{name}.mp3"
        if path.exists():
            _sounds[name] = pygame.mixer.Sound(str(path))


def play_music() -> None:
    """ Starts the background music on endless loop. """
    path = cfg.ASSETS_DIR / "music.mp3"
    if pygame.mixer.get_init() is None or not path.exists():
        return
    pygame.mixer.music.load(str(path))
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)


def play(name: str) -> None:
    sound = _sounds.get(name)
    if sound is not None:
        sound.play()
