import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1900
SCREEN_HEIGHT = 1600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(2, 5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)

# Game class
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Shooter")
        self.clock = pygame.time.Clock()
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player = Player()
        self.all_sprites.add(self.player)

        for _ in range(8):
            enemy = Enemy()
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bullet = Bullet(self.player.rect.centerx, self.player.rect.top)
                        self.all_sprites.add(bullet)
                        self.bullets.add(bullet)

            self.all_sprites.update()

            # Check for collisions
            hits = pygame.sprite.groupcollide(self.bullets, self.enemies, True, True)
            for hit in hits:
                enemy = Enemy()
                self.all_sprites.add(enemy)
                self.enemies.add(enemy)

            self.screen.fill(BLACK)
            self.all_sprites.draw(self.screen)
            pygame.display.flip()

        pygame.quit()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()
