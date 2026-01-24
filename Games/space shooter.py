import pygame
import random
from typing import List

pygame.init()
screen = pygame.display.set_mode((2560, 1800))
pygame.display.set_caption("Space Guardian — SCI-FI TPS Simulation")
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# ---- Configuration ----
WIDTH, HEIGHT = 800, 600
FPS = 60

PLAYER_SPEED = 5
PLAYER_FIRE_DELAY = 300  # milliseconds

ENEMY_ROWS = 3
ENEMY_COLS = 6
ENEMY_X_SPACING = 90
ENEMY_Y_SPACING = 60
ENEMY_START_X = 80
ENEMY_START_Y = 60
ENEMY_MOVE_SPEED = 1.0
ENEMY_DROP_AMOUNT = 10
ENEMY_FIRE_CHANCE_PER_SEC = 0.5  # per enemy (approx)

BULLET_SPEED = 7
ENEMY_BULLET_SPEED = 4

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (50, 200, 255)
ENEMY_COLOR = (255, 80, 80)
BULLET_COLOR = (255, 255, 100)
ENEMY_BULLET_COLOR = (255, 150, 150)


# ---- Sprites ----
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, dy: float, color=BULLET_COLOR):
        super().__init__()
        self.image = pygame.Surface((4, 12))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.dy = dy

    def update(self, dt):
        self.rect.y += self.dy * dt
        # Remove off-screen bullets
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
        pygame.draw.polygon(
            self.image,
            PLAYER_COLOR,
            [(0, 30), (20, 0), (40, 30)]
        )
        self.rect = self.image.get_rect(center=(x, y))
        self.last_shot_time = 0
        self.score = 0
        self.alive = True

    def update(self, keys, dt):
        if not self.alive:
            return
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = PLAYER_SPEED

        self.rect.x += dx * dt
        self.rect.y += dy * dt

        # Keep inside screen
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def can_shoot(self, now_ms):
        return (now_ms - self.last_shot_time) >= PLAYER_FIRE_DELAY

    def shoot(self, now_ms):
        self.last_shot_time = now_ms
        x = self.rect.centerx
        y = self.rect.top
        return Bullet(x, y, -BULLET_SPEED, BULLET_COLOR)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = pygame.Surface((44, 28))
        self.image.fill(ENEMY_COLOR)
        pygame.draw.rect(self.image, ENEMY_COLOR, (0, 0, 44, 28))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.alive = True

    def shoot(self):
        x = self.rect.centerx
        y = self.rect.bottom
        return Bullet(x, y, ENEMY_BULLET_SPEED, ENEMY_BULLET_COLOR)


# ---- Game functions ----
def create_enemy_group() -> List[Enemy]:
    enemies = []
    for r in range(ENEMY_ROWS):
        for c in range(ENEMY_COLS):
            x = ENEMY_START_X + c * ENEMY_X_SPACING
            y = ENEMY_START_Y + r * ENEMY_Y_SPACING
            enemies.append(Enemy(x, y))
    return enemies


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Shooter (Simple)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    # Sprite groups
    player_group = pygame.sprite.Group()
    player = Player(WIDTH // 2, HEIGHT - 60)
    player_group.add(player)

    enemy_group = pygame.sprite.Group()
    enemies = create_enemy_group()
    for e in enemies:
        enemy_group.add(e)

    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()

    # Enemy movement state
    enemy_direction = 1  # 1 = right, -1 = left
    enemy_move_timer = 0.0

    running = True
    while running:
        dt_raw = clock.tick(FPS)
        dt = dt_raw / 16.6667  # normalize to ~60FPS movement scale (so speed constants feel similar)
        now_ms = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        # Player update & input
        player.update(keys, dt)
        if (keys[pygame.K_SPACE] or keys[pygame.K_z]) and player.can_shoot(now_ms):
            player_bullets.add(player.shoot(now_ms))

        # Enemy movement: move as a block (classic style)
        # Determine bounds of enemies
        if len(enemy_group.sprites()) > 0:
            leftmost = min(e.rect.left for e in enemy_group.sprites())
            rightmost = max(e.rect.right for e in enemy_group.sprites())
            # If hitting edges, reverse and drop
            if rightmost + ENEMY_MOVE_SPEED * enemy_direction * dt > WIDTH - 10 and enemy_direction == 1:
                enemy_direction = -1
                for e in enemy_group.sprites():
                    e.rect.y += ENEMY_DROP_AMOUNT
            elif leftmost + ENEMY_MOVE_SPEED * enemy_direction * dt < 10 and enemy_direction == -1:
                enemy_direction = 1
                for e in enemy_group.sprites():
                    e.rect.y += ENEMY_DROP_AMOUNT

            # Move horizontally
            for e in enemy_group.sprites():
                e.rect.x += ENEMY_MOVE_SPEED * enemy_direction * dt

        # Enemies randomly shoot
        for e in enemy_group.sprites():
            # Based on probability per frame computed from chance per second
            prob_per_frame = ENEMY_FIRE_CHANCE_PER_SEC / FPS
            if random.random() < prob_per_frame:
                enemy_bullets.add(e.shoot())

        # Update bullets
        player_bullets.update(dt_raw / (1000 / FPS))
        enemy_bullets.update(dt_raw / (1000 / FPS))

        # Collisions: player bullets vs enemies
        hits = pygame.sprite.groupcollide(enemy_group, player_bullets, True, True)
        if hits:
            for hit_enemy in hits:
                player.score += 100

        # Enemy bullets vs player
        if pygame.sprite.spritecollide(player, enemy_bullets, True):
            player.alive = False

        # Enemies reaching player bottom -> game over
        for e in enemy_group.sprites():
            if e.rect.bottom >= player.rect.top:
                player.alive = False

        # Clear screen
        screen.fill(BLACK)

        # Draw sprites
        enemy_group.draw(screen)
        player_group.draw(screen)
        player_bullets.draw(screen)
        enemy_bullets.draw(screen)

        # HUD
        score_surf = font.render(f"Score: {player.score}", True, WHITE)
        screen.blit(score_surf, (8, 8))

        if not player.alive:
            over_surf = font.render("GAME OVER - Press ESC to quit", True, WHITE)
            screen.blit(over_surf, (WIDTH // 2 - over_surf.get_width() // 2, HEIGHT // 2))

        # Win condition
        if len(enemy_group) == 0:
            win_surf = font.render("YOU WIN! - Press ESC to quit", True, WHITE)
            screen.blit(win_surf, (WIDTH // 2 - win_surf.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
