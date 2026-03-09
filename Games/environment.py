import pygame
pygame.init()

if __name__ == "__main__":
    pygame.init()



# ---- Configuration ----
WIDTH, HEIGHT = 2560, 1600
FPS = 60

pygame.init()

PLAYER_START_X = WIDTH // 2
PLAYER_START_Y = HEIGHT - 140
PLAYER_SIZE = 40

PLAYER_MOVE_SPEED = 400.0
PLAYER_INITIAL_HEALTH = 150  # Player needs 150 hits to die

ENEMY_ROWS, ENEMY_COLS = 3, 6
ENEMY_X_SPACING, ENEMY_Y_SPACING = 120, 100
ENEMY_START_X = 100
ENEMY_START_Y = 30
ENEMY_INITIAL_HEALTH = 26  # Enemies need 26 hits to die

PLAYER_BULLET_SPEED = 500
ENEMY_BULLET_SPEED = 300

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (50, 200, 255)
ENEMY_COLOR = (255, 80, 80)
BULLET_COLOR = (255, 255, 100)
ENEMY_BULLET_COLOR = (255, 150, 150)
HEALTH_COLOR = (0, 255, 0)
DAMAGE_COLOR = (255, 0, 0)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(BULLET_COLOR)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self, dt):
        self.rect.y -= self.speed * dt
        if self.rect.bottom < 0:
            self.kill()  # Remove bullet if it goes off-screen  

player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()



class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = PLAYER_MOVE_SPEED
        self.health = PLAYER_INITIAL_HEALTH

    def update(self, keys, dt):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed * dt
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed * dt
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed * dt
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed * dt

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top, PLAYER_BULLET_SPEED)
        player_bullets.add(bullet)

    def draw_health_bar(self, surface):
        bar_width = 100
        bar_height = 10
        health_percentage = self.health / PLAYER_INITIAL_HEALTH

        pygame.draw.rect(surface, (255, 0, 0), (self.rect.x, self.rect.y - 15, bar_width, bar_height))  # Red background
        pygame.draw.rect(surface, (0, 255, 0), (self.rect.x, self.rect.y - 15, bar_width * health_percentage, bar_height))  # Green foreground


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill(ENEMY_COLOR)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = ENEMY_INITIAL_HEALTH
        self.max_health = ENEMY_INITIAL_HEALTH

    def shoot(self):
        # Calculate the direction towards the player
        bullet = Bullet(self.rect.centerx, self.rect.bottom, ENEMY_BULLET_SPEED)
        bullet.dy = ENEMY_BULLET_SPEED  # Set the bullet speed to move downwards
        return bullet


    def take_damage(self, dmg=1):
        self.health -= dmg
        if self.health <= 0:
            self.kill()
            return True  # Enemy died
        return False  # Enemy still alive

    def draw_health_bar(self, surface):
        bar_width = self.rect.width
        bar_height = 5
        bar_x = self.rect.left
        bar_y = self.rect.top - bar_height - 2
        pygame.draw.rect(surface, (200, 30, 30), (bar_x, bar_y, bar_width, bar_height))
        health_width = int(bar_width * (self.health / self.max_health))
        if health_width > 0:
            pygame.draw.rect(surface, (30, 220, 30), (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)


# Create enemy instances
enemies = pygame.sprite.Group()
for row in range(ENEMY_ROWS):
    for col in range(ENEMY_COLS):
        enemy_x = ENEMY_START_X + col * ENEMY_X_SPACING
        enemy_y = ENEMY_START_Y + row * ENEMY_Y_SPACING
        enemies.add(Enemy(enemy_x, enemy_y))


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.player = Player(WIDTH // 2, HEIGHT - 140)  # Centered player
        self.player_group = pygame.sprite.Group(self.player)

    def update(self):
        dt = self.clock.get_time() / 1000.0  # Convert milliseconds to seconds
        keys = pygame.key.get_pressed()
        self.player.update(keys, dt)  # Update player

        # Update bullets
        player_bullets.update(dt)
        enemy_bullets.update(dt)

        # Check for collisions
        for bullet in player_bullets:
            hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)
            for enemy in hit_enemies:
                enemy.take_damage(1)
                bullet.kill()  # Remove bullet after hitting

        for enemy in enemies:
            # Example of enemy shooting logic (could be refined)
            if pygame.time.get_ticks() % 1000 == 50:  # Shoot every second
                enemy_bullets.add(enemy.shoot())

    def draw(self):
        self.screen.fill(BLACK)  # Clear the screen with black
        self.player_group.draw(self.screen)  # Draw the player
        player_bullets.draw(self.screen)  # Draw player bullets
        enemies.draw(self.screen)  # Draw enemies
        enemy_bullets.draw(self.screen)  # Draw enemy bullets

        self.player.draw_health_bar(self.screen)  # Draw player health bar
        for enemy in enemies:
            enemy.draw_health_bar(self.screen)  # Draw enemy health bars

        pygame.display.flip()  # Update the full display Surface to the screen

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  # Shoot bullet on space
                        self.player.shoot()

            self.update()  # Update game state
            self.draw()    # Draw everything on the screen

            self.clock.tick(FPS)  # Limit to FPS

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()