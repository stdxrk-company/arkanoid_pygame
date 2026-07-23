"""screens/game_screen.py – main gameplay screen: level, bonuses, lives and score."""

import pygame

import settings as cfg
from game import audio
from game.entities import Ball, Bonus, Brick, LaserBullet, Paddle
from game.level import load_level


def _bounce_off_rect(ball: Ball, rect: pygame.Rect) -> None:
    """ Bounces the Ball off the given rect (side with the smallest overlap). """

    overlap_left = ball.rect.right - rect.left
    overlap_right = rect.right - ball.rect.left
    overlap_top = ball.rect.bottom - rect.top
    overlap_bottom = rect.bottom - ball.rect.top

    min_overlap = min(
        overlap_bottom,
        overlap_left,
        overlap_right,
        overlap_top)

    if min_overlap == overlap_top and ball.vy > 0:
        ball.rect.bottom = rect.top
        ball.vy *= -1
    elif min_overlap == overlap_bottom and ball.vy < 0:
        ball.rect.top = rect.bottom
        ball.vy *= -1
    elif min_overlap == overlap_left and ball.vx > 0:
        ball.rect.right = rect.left
        ball.vx *= -1
    elif min_overlap == overlap_right and ball.vx < 0:
        ball.rect.left = rect.right
        ball.vx *= -1


class GameScreen:
    """ Owns all gameplay state and runs the main loop for one level. """

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, level: int) -> None:
        self.screen = screen
        self.clock = clock
        self.level = level

        self.paddle = Paddle()
        self.bricks, _, _ = load_level(level)
        self.balls: list[Ball] = [self._new_ball()]
        self.bonuses: list[Bonus] = []
        self.bullets: list[LaserBullet] = []

        self.score = 0
        self.lives = cfg.START_LIVES
        self.hud_font = pygame.font.Font(None, 28)

    # --- Loop ----------------------------------------------------------------

    def run(self) -> bool:
        """ Runs the level. Returns False if the window was closed, True otherwise. """
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # Back to the menu
                        return True
                    if event.key == pygame.K_SPACE and self.paddle.laser:
                        self._shoot()

            self._update()
            self._draw()

            pygame.display.flip()
            self.clock.tick(cfg.FPS)

            if self._level_cleared():
                self._show_message("YOU WIN!")
                return True
            if self.lives <= 0:
                self._show_message("GAME OVER")
                return True

    def _update(self) -> None:
        self.paddle.move(pygame.key.get_pressed())

        for ball in self.balls[:]:
            ball.update()
            self._handle_ball_vs_bricks(ball)
            if ball.rect.colliderect(self.paddle.rect) and ball.vy > 0:
                self._handle_ball_vs_paddle(ball)
            if ball.rect.top > cfg.HEIGHT:  # Ball is lost
                self.balls.remove(ball)

        if not self.balls:  # All balls are lost - lose a life
            self.lives -= 1
            if self.lives > 0:
                self.balls.append(self._new_ball())

        for bonus in self.bonuses[:]:
            bonus.update()
            if bonus.rect.colliderect(self.paddle.rect):
                audio.play("bonus")
                self.apply_bonus(bonus.type)
                self.bonuses.remove(bonus)
            elif bonus.rect.top > cfg.HEIGHT:
                self.bonuses.remove(bonus)

        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.rect.bottom < 0:
                self.bullets.remove(bullet)
                continue
            for brick in self.bricks:
                if bullet.rect.colliderect(brick.rect):
                    if brick.hp > 0:
                        self._hit_brick(brick)
                    self.bullets.remove(bullet)
                    break

    def _draw(self) -> None:
        self.screen.fill(cfg.BLACK)

        for brick in self.bricks:
            brick.draw(self.screen)
        for bonus in self.bonuses:
            bonus.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        self.paddle.draw(self.screen)
        for ball in self.balls:
            ball.draw(self.screen)

        score_text = self.hud_font.render(f"Score: {self.score}", True, cfg.WHITE)
        lives_text = self.hud_font.render(f"Lives: {self.lives}", True, cfg.WHITE)
        self.screen.blit(score_text, (cfg.FIELD_LEFT, 12))
        self.screen.blit(lives_text, lives_text.get_rect(topright=(cfg.FIELD_RIGHT, 12)))

    # --- Bonuses -------------------------------------------------------------

    def apply_bonus(self, bonus_type: str) -> None:
        """ Applies the effect of a bonus caught by the paddle. """
        if bonus_type == "extend":
            self.paddle.extend()
        elif bonus_type == "shrink":
            self.paddle.shrink()
        elif bonus_type == "multiball":
            self._spawn_extra_balls()
        elif bonus_type == "laser":
            self.paddle.laser = True
        elif bonus_type == "extra_life":
            self.lives += 1
        elif bonus_type == "speed_up":
            for ball in self.balls:
                ball.scale_speed(cfg.BALL_SPEED_UP_FACTOR)
        elif bonus_type == "speed_down":
            for ball in self.balls:
                ball.scale_speed(cfg.BALL_SPEED_DOWN_FACTOR)

    def _spawn_extra_balls(self) -> None:
        source = self.balls[0]
        for vx in (-cfg.BALL_SPEED_X, cfg.BALL_SPEED_X):
            ball = Ball(*source.rect.center)
            ball.vx = vx
            ball.vy = -abs(source.vy)
            self.balls.append(ball)

    def _shoot(self) -> None:
        audio.play("laser")
        for x in (self.paddle.rect.left + 7, self.paddle.rect.right - 7):
            self.bullets.append(LaserBullet(x, self.paddle.rect.top))

    # --- Collisions ----------------------------------------------------------

    def _handle_ball_vs_bricks(self, ball: Ball) -> None:
        for brick in self.bricks[:]:
            if not ball.rect.colliderect(brick.rect):
                continue
            _bounce_off_rect(ball, brick.rect)
            if brick.hp > 0:  # Walls (-1) and armored bricks (0) are unbreakable
                self._hit_brick(brick)

    def _hit_brick(self, brick: Brick) -> None:
        audio.play("hit")
        bonus_type = brick.hit()
        if bonus_type:
            self.bonuses.append(Bonus(brick.rect.center, bonus_type))
        if brick.hp == 0:  # Brick is destroyed
            self.bricks.remove(brick)
            self.score += 10

    def _handle_ball_vs_paddle(self, ball: Ball) -> None:
        """ Bounces the Ball off the Paddle, angle depends on the hit point. """
        audio.play("hit")
        _bounce_off_rect(ball, self.paddle.rect)
        offset = (ball.rect.centerx - self.paddle.rect.centerx) / (self.paddle.rect.width / 2)
        max_vx = cfg.MAX_BALL_SPEED_X
        ball.vx = max(-max_vx, min(max_vx, offset * max_vx))

    # --- Helpers -------------------------------------------------------------

    def _new_ball(self) -> Ball:
        return Ball(self.paddle.rect.centerx, self.paddle.rect.top - cfg.BALL_RADIUS)

    def _level_cleared(self) -> bool:
        return not any(brick.hp > 0 for brick in self.bricks)

    def _show_message(self, message: str) -> None:
        font = pygame.font.Font(None, 72)
        text = font.render(message, True, cfg.WHITE)
        self.screen.blit(text, text.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2)))
        pygame.display.flip()
        pygame.time.wait(2000)


def run(screen: pygame.Surface, clock: pygame.time.Clock, level: int) -> bool:
    return GameScreen(screen, clock, level).run()
