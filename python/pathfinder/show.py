import pygame
import sys

from .grid import (
    Tile
)

from .grid import (
    PathScene,
    PathWay
)

from .pathfinder import PathFinder

class ShowPathFinder:

    _pathfinder : PathFinder
    _pathscene : PathScene
    _path_way : PathWay

    _tiles_grid : list[list[Tile]]
    _grid_height : int
    _grid_width : int

    def __init__(
            self, 
            pathfinder : PathFinder):
        
        self._pathfinder = pathfinder
        self._pathscene = pathfinder._pathscene
        self._path_way = pathfinder._path_way

        self._tiles_grid = self._pathscene.grid(horizontal=True)
        self._grid_height = len(self._tiles_grid)
        self._grid_width = len(self._tiles_grid[0])

        self._scale_multiplier = 50
        self._window_width = self._grid_width * self._scale_multiplier
        self._window_height = self._grid_height * self._scale_multiplier

        self._block_size = (self._window_width / self._grid_width)

        pygame.init()
        self._screen = pygame.display.set_mode((self._window_width, self._window_height))
        pygame.display.set_caption("Grid Scenery")
    
    def _draw_text(self, text, x, y):

        # Render the text
        FONT_SIZE = 24
        FONT_COLOR = (255, 255, 255)

        font = pygame.font.Font(None, FONT_SIZE)

        text_surface = font.render(text, True, FONT_COLOR)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)

        # Draw the text on the screen
        self._screen.blit(text_surface, text_rect)

    def _draw_grid(self, grid):
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):

                if cell == Tile.EMPTY:
                    continue

                pygame.draw.rect(
                    self._screen, 
                    cell.value.color, (
                        x * self._block_size, 
                        y * self._block_size, 
                        self._block_size, 
                        self._block_size)
                )

    def _draw_grid_lines(self):

        for i in range(self._grid_width):
            pygame.draw.line(
                self._screen, 
                (100, 100, 100), 
                (i * self._block_size, 0), 
                (i * self._block_size, self._window_height)
            )

        for i in range(self._grid_height):
            pygame.draw.line(
                self._screen, 
                (100, 100, 100), 
                (0, i * self._block_size), 
                (self._window_width, i * self._block_size)
            )

        # draw a rect on the cursor block position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tile_coord_x = int(mouse_x / self._block_size)
        tile_coord_y = (int(mouse_y / self._block_size))

        pygame.draw.rect(
            self._screen, 
            (50, 50, 50), (
                tile_coord_x * self._block_size, 
                tile_coord_y * self._block_size, 
                self._block_size, 
                self._block_size)
        )



    def _draw_cursor_text(self):

        mouse_x, mouse_y = pygame.mouse.get_pos()

        tile_coord_x = int(mouse_x / self._block_size)
        tile_coord_y = abs(int(mouse_y / self._block_size) - self._grid_height) - 1

        self._draw_text(f"({tile_coord_x}, {tile_coord_y})", mouse_x, mouse_y)

    def show(self):

        # Main game loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self._screen.fill((0, 0, 0))
            self._draw_grid(self._tiles_grid)
            self._draw_grid_lines()
            self._draw_cursor_text()

            pygame.display.flip()

        # Quit Pygame
        pygame.quit()
        sys.exit(0)