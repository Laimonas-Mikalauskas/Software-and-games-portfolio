import pygame
import random
from typing import List


class Settings:
    """Application configuration and constants."""

    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    CELL_SIZE = 10

    FPS = 12

    ROWS = WINDOW_HEIGHT // CELL_SIZE
    COLS = WINDOW_WIDTH // CELL_SIZE

    BACKGROUND_COLOR = (20, 20, 20)
    CELL_COLOR = (230, 230, 230)
    GRID_COLOR = (50, 50, 50)


class Grid:
    """Handles simulation logic and grid state."""

    def __init__(self) -> None:
        self.rows = Settings.ROWS
        self.cols = Settings.COLS
        self.grid: List[List[int]] = self._generate_random_grid()

    def _generate_random_grid(self) -> List[List[int]]:
        """Create initial randomized grid."""
        return [
            [random.choice([0, 1]) for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

    def clear(self) -> None:
        """Reset grid to empty state."""
        self.grid = [[0 for _ in range(self.cols)]
                     for _ in range(self.rows)]

    def toggle_cell(self, mouse_x: int, mouse_y: int) -> None:
        """Activate cell using mouse coordinates."""
        col = mouse_x // Settings.CELL_SIZE
        row = mouse_y // Settings.CELL_SIZE

        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row][col] = 1

    def update(self) -> None:
        """Apply Conway's rules and update grid state."""
        new_grid = [[0 for _ in range(self.cols)]
                    for _ in range(self.rows)]

        for row in range(self.rows):
            for col in range(self.cols):
                neighbors = self._count_neighbors(row, col)
                cell_alive = self.grid[row][col] == 1

                if cell_alive and neighbors in (2, 3):
                    new_grid[row][col] = 1

                if not cell_alive and neighbors == 3:
                    new_grid[row][col] = 1

        self.grid = new_grid

    def _count_neighbors(self, row: int, col: int) -> int:
        """Count alive neighbors for a given cell."""
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]

        count = 0

        for dx, dy in directions:
            r = row + dx
            c = col + dy

            if 0 <= r < self.rows and 0 <= c < self.cols:
                count += self.grid[r][c]

        return count


class Renderer:
    """Responsible for drawing grid and UI elements."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen

    def draw(self, grid: Grid) -> None:
        self.screen.fill(Settings.BACKGROUND_COLOR)

        for row in range(grid.rows):
            for col in range(grid.cols):
                if grid.grid[row][col]:
                    pygame.draw.rect(
                        self.screen,
                        Settings.CELL_COLOR,
                        (
                            col * Settings.CELL_SIZE,
                            row * Settings.CELL_SIZE,
                            Settings.CELL_SIZE,
                            Settings.CELL_SIZE
                        )
                    )

        self._draw_grid_lines()

    def _draw_grid_lines(self) -> None:
        for x in range(0, Settings.WINDOW_WIDTH, Settings.CELL_SIZE):
            pygame.draw.line(
                self.screen,
                Settings.GRID_COLOR,
                (x, 0),
                (x, Settings.WINDOW_HEIGHT)
            )

        for y in range(0, Settings.WINDOW_HEIGHT, Settings.CELL_SIZE):
            pygame.draw.line(
                self.screen,
                Settings.GRID_COLOR,
                (0, y),
                (Settings.WINDOW_WIDTH, y)
            )


class Game:
    """Main application controller."""

    def __init__(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode(
            (Settings.WINDOW_WIDTH, Settings.WINDOW_HEIGHT)
        )

        pygame.display.set_caption("Conway's Game of Life — OOP Simulation")

        self.clock = pygame.time.Clock()

        self.grid = Grid()
        self.renderer = Renderer(self.screen)

        self.running = True
        self.paused = False

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            self.clock.tick(Settings.FPS)

            self._handle_events()
            self._update()
            self._render()

        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused

                if event.key == pygame.K_r:
                    self.grid.clear()

        if pygame.mouse.get_pressed()[0]:
            x, y = pygame.mouse.get_pos()
            self.grid.toggle_cell(x, y)

    def _update(self) -> None:
        if not self.paused:
            self.grid.update()

    def _render(self) -> None:
        self.renderer.draw(self.grid)
        pygame.display.update()


if __name__ == "__main__":
    app = Game()
    app.run()






    

  





























































































