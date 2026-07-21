import pygame
import settings as cfg
from screens.game_screen import run as game_screen
from game.entities import Paddle, Brick, Ball

def main():
    pygame.init()
    screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
    pygame.display.set_caption("Arkanoid")
    clock = pygame.time.Clock()

    running = True
    paddle = Paddle()
    bricks = [
        Brick(2, 2, 1),
        Brick(1, 5, 2),
        Brick(2, 1, 0),
        Brick(0, 0, -1)
    ]
    ball = Ball(cfg.WIDTH // 2, cfg.HEIGHT // 2)

    while running:
        # Main Loop
        screen.fill(cfg.BLACK)

        # Update Section
        keys = pygame.key.get_pressed()

        paddle.move(keys)
        ball.update()

        # Draw Section
        paddle.draw(screen)
        ball.draw(screen)

        for brick in bricks:
            brick.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:   # Press "close" button
                running = False

        pygame.display.flip()   # Screen Update
        clock.tick(cfg.FPS)         # FPS (Frames Per Second)

    pygame.quit()

if __name__ == "__main__":
    main()
