import pygame
import random
from typing import List


class Settings:
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    CELL_SIZE = 8
    FPS = 12

    ROWS = WINDOW_HEIGHT // CELL_SIZE
    COLS = WINDOW_WIDTH // CELL_SIZE

    BACKGROUND_COLOR = (20, 20, 20)
    CELL_COLOR = (230, 230, 230)
    GRID_COLOR = (50, 50, 50)


class Grid:
    def __init__(self) -> None:
        self.rows = Settings.ROWS
        self.cols = Settings.COLS
        self.grid: List[List[int]] = self._generate_random_grid()

    def _generate_random_grid(self) -> List[List[int]]:
        return [
            [1 if random.random() > 0.82 else 0 for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

    def clear(self) -> None:
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    def randomize(self) -> None:
        self.grid = self._generate_random_grid()

    def set_cell(self, mouse_x: int, mouse_y: int, value: int) -> None:
        col = mouse_x // Settings.CELL_SIZE
        row = mouse_y // Settings.CELL_SIZE
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row][col] = value

    def toggle_cell(self, mouse_x: int, mouse_y: int) -> None:
        col = mouse_x // Settings.CELL_SIZE
        row = mouse_y // Settings.CELL_SIZE
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row][col] = 1 - self.grid[row][col]

    def update(self) -> None:
        new_grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        for row in range(self.rows):
            for col in range(self.cols):
                neighbors = self._count_neighbors(row, col)
                alive = self.grid[row][col] == 1
                if alive and neighbors in (2, 3):
                    new_grid[row][col] = 1
                if not alive and neighbors == 3:
                    new_grid[row][col] = 1
        self.grid = new_grid

    def _count_neighbors(self, row: int, col: int) -> int:
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
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.show_grid = True

    def draw(self, grid: Grid) -> None:
        self.screen.fill(Settings.BACKGROUND_COLOR)
        cell_size = Settings.CELL_SIZE
        for row in range(grid.rows):
            for col in range(grid.cols):
                if grid.grid[row][col]:
                    pygame.draw.rect(
                        self.screen,
                        Settings.CELL_COLOR,
                        (col * cell_size, row * cell_size, cell_size, cell_size)
                    )
        if self.show_grid:
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
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(
            (Settings.WINDOW_WIDTH, Settings.WINDOW_HEIGHT)
        )
        pygame.display.set_caption("Conway's Game of Life — OOP")
        self.clock = pygame.time.Clock()
        self.grid = Grid()
        self.renderer = Renderer(self.screen)
        self.running = True
        self.paused = False
        self.ticks = 0

        # painting state for click-and-drag
        self.painting = False
        self.paint_value = 1  # 1 = paint alive, 0 = erase

    def run(self) -> None:
        while self.running:
            self.clock.tick(Settings.FPS)
            self._handle_events()
            if not self.paused:
                self.grid.update()
            self._render()
        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.grid.clear()
                elif event.key == pygame.K_n:
                    self.grid.randomize()
                elif event.key == pygame.K_g:
                    self.renderer.show_grid = not self.renderer.show_grid

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left click -> paint alive
                    self.painting = True
                    self.paint_value = 1
                    x, y = event.pos
                    self.grid.set_cell(x, y, 1)
                elif event.button == 3:  # right click -> erase
                    self.painting = True
                    self.paint_value = 0
                    x, y = event.pos
                    self.grid.set_cell(x, y, 0)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button in (1, 3):
                    self.painting = False

            elif event.type == pygame.MOUSEMOTION:
                if self.painting:
                    x, y = event.pos
                    self.grid.set_cell(x, y, self.paint_value)

    def _render(self) -> None:
        self.renderer.draw(self.grid)
        pygame.display.flip()
        self.ticks += 1
        pygame.display.set_caption(
            f"Conway's Game of Life — ticks={self.ticks} {'(paused)' if self.paused else ''}"
        )


if __name__ == "__main__":
    app = Game()
    app.run()

    
