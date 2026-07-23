"""game/entities.py – basic game entities."""

import random
from collections import deque

import pygame

import settings as cfg


class Paddle:
    """ Paddle actor: moves horizontally and bounces off the ball. """

    def __init__(self) -> None:
        self.rect = pygame.Rect(0, 0, cfg.PADDLE_WIDTH, cfg.PADDLE_HEIGHT)
        self.rect.midbottom = (cfg.WIDTH // 2, cfg.HEIGHT - 20)
        self.speed = cfg.PADDLE_SPEED
        self.vx = 0
        self.laser = False

    def move(self, keys: pygame.key.ScancodeWrapper) -> None:
        self.vx = 0
        if keys[pygame.K_LEFT]:
            self.vx = -self.speed
        elif keys[pygame.K_RIGHT]:
            self.vx = self.speed
        self.rect.x += self.vx
        if self.rect.left < cfg.FIELD_LEFT:
            self.rect.left = cfg.FIELD_LEFT
        if self.rect.right > cfg.FIELD_RIGHT:
            self.rect.right = cfg.FIELD_RIGHT

    def extend(self) -> None:
        """ Bonus: makes the paddle wider. """
        self._resize(round(self.rect.width * cfg.PADDLE_RESIZE_FACTOR))

    def shrink(self) -> None:
        """ Bonus: makes the paddle narrower. """
        self._resize(round(self.rect.width / cfg.PADDLE_RESIZE_FACTOR))

    def _resize(self, new_width: int) -> None:
        center_x = self.rect.centerx
        self.rect.width = max(cfg.PADDLE_MIN_WIDTH, min(cfg.PADDLE_MAX_WIDTH, new_width))
        self.rect.centerx = center_x
        # Keep the paddle inside the field after resizing
        if self.rect.left < cfg.FIELD_LEFT:
            self.rect.left = cfg.FIELD_LEFT
        if self.rect.right > cfg.FIELD_RIGHT:
            self.rect.right = cfg.FIELD_RIGHT

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, cfg.PADDLE_COLOR, self.rect, border_radius=5)
        if self.laser:
            # Small turrets on the paddle edges while the laser is active
            for x in (self.rect.left + 4, self.rect.right - 10):
                pygame.draw.rect(screen, cfg.YELLOW, pygame.Rect(x, self.rect.top - 6, 6, 6))


class Ball:
    """ Ball: basic physics, bounces off the rects. """

    def __init__(self, x: int, y: int) -> None:
        self.radius = cfg.BALL_RADIUS
        self.rect = pygame.Rect(x - self.radius, y - self.radius, 2 * self.radius, 2 * self.radius)
        self.vx = cfg.BALL_SPEED_X
        self.vy = cfg.BALL_SPEED_Y

        self.trail: deque[tuple[int, int]] = deque(maxlen=cfg.TRAIL_LENGTH)

    def update(self) -> None:
        self.trail.append(self.rect.center)
        self.rect.x += self.vx
        self.rect.y += self.vy

    def scale_speed(self, factor: float) -> None:
        """ Bonus: scales the ball speed, keeping the direction. """
        self.vx *= factor
        self.vy *= factor
        # Clamp the speed so the ball never stalls or becomes uncatchable
        self.vx = max(-cfg.MAX_BALL_SPEED_X, min(cfg.MAX_BALL_SPEED_X, self.vx))
        vy_mag = max(cfg.BALL_MIN_SPEED_Y, min(cfg.BALL_MAX_SPEED_Y, abs(self.vy)))
        self.vy = vy_mag if self.vy > 0 else -vy_mag

    def draw(self, screen: pygame.Surface) -> None:
        trail_len = len(self.trail)
        for i, pos in enumerate(self.trail):
            fade = (i + 1) / (trail_len + 1) 
            color = tuple(int(channel * fade) for channel in cfg.BALL_COLOR)
            pygame.draw.circle(screen, color, pos, self.radius)
        pygame.draw.circle(screen, cfg.BALL_COLOR, self.rect.center, self.radius)


class Brick:
    """
    Brick object, level boundary.
    """

    def __init__(self, col: int, row: int, hp: int) -> None:
        self.hp = hp
        self.max_hp = hp if hp > 0 else 0
        self.color = cfg.BRICK_COLORS[hp]
        self.rect = pygame.Rect(
            cfg.FIELD_LEFT + col * cfg.BRICK_WIDTH,
            cfg.TOP_OFFSET + row * cfg.BRICK_HEIGHT,
            cfg.BRICK_WIDTH,
            cfg.BRICK_HEIGHT,
        )

    def hit(self) -> str | None:
        """Handles the Brick hit. Returns bonus type or None."""
        if self.hp > 0:
            self.hp -= 1
            if self.hp > 0:
                self.color = cfg.BRICK_COLORS[self.hp]
                return None
            # Brick is destroyed, there's a chance to drop a bonus
            if random.random() < cfg.BONUS_PROBABILITY:
                return random.choice(cfg.BONUS_TYPES)
        return None

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, cfg.DARK_GRAY, self.rect, 2)  # рамка


class Bonus:
    """ Bonus emitted from a destroyed block. """

    TYPES = {
        "extend": {"color": cfg.GREEN, "letter": "E"},
        "multiball": {"color": cfg.MAGENTA, "letter": "M"},
        "laser": {"color": cfg.YELLOW, "letter": "L"},
        "extra_life": {"color": cfg.CYAN, "letter": "1"},
        "shrink": {"color": cfg.RED, "letter": "S"},
        "speed_up": {"color": cfg.ORANGE, "letter": "+"},
        "speed_down": {"color": cfg.WHITE, "letter": "-"},
    }

    _label_font: pygame.font.Font | None = None  # Lazy Creation

    def __init__(self, center: tuple[int, int], bonus_type: str) -> None:
        self.type = bonus_type
        self.rect = pygame.Rect(0, 0, 24, 24)
        self.rect.center = center
        self.vy = 3
        props = Bonus.TYPES[bonus_type]
        self.color = props["color"]
        self.letter = props["letter"]

    @classmethod
    def _get_label_font(cls) -> pygame.font.Font:
        if cls._label_font is None:
            cls._label_font = pygame.font.Font(None, 24)
        return cls._label_font

    def update(self) -> None:
        self.rect.y += self.vy

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
        text = self._get_label_font().render(self.letter, True, cfg.BLACK)
        screen.blit(text, text.get_rect(center=self.rect.center))


class LaserBullet:
    """ Laser Bullet, flies upwards and destroys bricks. """

    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(x - 2, y, 4, 10)
        self.vy = -10

    def update(self) -> None:
        self.rect.y += self.vy

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, cfg.YELLOW, self.rect)
