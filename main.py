import pygame

import time
import pathlib
import random

pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800

ASSETS_DIR = pathlib.Path(__file__).parent / "assets"


def _load_image(img_path: pathlib.Path) -> pygame.Surface:
    return pygame.transform.scale2x(pygame.image.load(img_path))


BIRD_IMGS = [_load_image(ASSETS_DIR / f"bird{i}.png") for i in range(1, 4)]
PIPE_IMG = _load_image(ASSETS_DIR / "pipe.png")
BASE_IMG = _load_image(ASSETS_DIR / "base.png")
BG_IMG = _load_image(ASSETS_DIR / "bg.png")

STAT_FONT = pygame.font.SysFont("arial", 50)


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25  # how much bird is going to tilt
    ROT_VEL = 20  # how much bird we're gonna rotate on each frame
    ANIMATION_TIME = 5  # how much time bird is going to stay on the same image

    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -9.5
        self.tick_count = 0  # when we last jumped
        self.height = self.y

    def move(self):
        self.tick_count += 1

        # displacement
        # d = v*t + 3/2*t^2
        d = self.vel * self.tick_count + 1.5 * self.tick_count**2

        # naive "terminal velocity"
        if d >= 16:
            d = 16
        elif d < 0:
            d -= 2

        self.y = self.y + d

        # rotation
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        elif self.tilt > -90:
            self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count >= self.ANIMATION_TIME * 3 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        # This is just how we rotate image in pygame
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(
            center=self.img.get_rect(topleft=(self.x, self.y)).center
        )
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200  # how much space is between two pipes
    VEL = 5  # how fast are the pipes moving;

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0  # where top is gonna be drawn
        self.bottom = 0  # where bottom is gonna be drawn
        # img top pipe
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, flip_x=False, flip_y=True)
        # img bottom pipe
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False  # if bird passed the pipe; for collision detection
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL  # move pipe to the left by `self.VEL` velocity

    def draw(self, win: pygame.Surface):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird: Bird) -> bool:
        """Utilize pygame.mask to implement pixel-perfect collision."""
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        # Use `round` below because offset has to be int.
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        bottom_overlap = bird_mask.overlap(bottom_mask, bottom_offset)
        top_verlap = bird_mask.overlap(top_mask, top_offset)

        if top_verlap or bottom_overlap:
            return True
        return False


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # If first base image is out of the game window, move it behind the
        # second one. Similarly for the second base image. Repeat this cycle
        # until end of game.
        if (self.x1 + self.WIDTH) < 0:
            self.x1 = self.x2 + self.WIDTH
        if (self.x2 + self.WIDTH) < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win: pygame.Surface):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(
    win: pygame.Surface,
    bird: Bird,
    pipes: list[Pipe],
    base: Base,
    score: int,
):
    win.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render(f"Score: {score}", 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    # win.blitting base and bird.
    base.draw(win)
    bird.draw(win)

    pygame.display.update()


def game_over():
    time.sleep(1)
    pygame.quit()
    quit()


def main():
    base_x = 730
    pipe_x = 600

    bird = Bird(x=230, y=350)
    base = Base(base_x)
    pipes = [Pipe(pipe_x)]

    score = 0
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()

        bird.move()

        for pipe in pipes:
            if pipe.collide(bird):
                game_over()

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                # pipe is out of the game window
                pipes.remove(pipe)
                pipes.append(Pipe(pipe_x))

            if pipe.x < bird.x and not pipe.passed:
                pipe.passed = True
                score += 1

        for pipe in pipes:
            pipe.move()

        # Bird hit the floor.
        if bird.y + bird.img.get_height() >= base_x:
            game_over()

        base.move()
        draw_window(win, bird, pipes, base, score)
        print(score)

    pygame.quit()


if __name__ == "__main__":
    main()
