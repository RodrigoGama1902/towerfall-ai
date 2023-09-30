import pygame
import sys
import math

from .grid import (
    Tile
)

from .grid import (
    PathScene,
    PathWay
)

from .pathfinder import PathFinder

# Function to calculate distance between two points
def calculate_distance(point1, point2):
    return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)


class LineMeasure:

    _font : pygame.font.Font

    _drawing: bool
    _start_pos : tuple[int, int]
    _end_pos : tuple[int, int]
    _distance : int
    _distance_text : None | pygame.Surface
    _block_size : float

    def __init__(
            self, 
            block_size : float,
            font_size= 24, 
            line_color : tuple[int, int, int] = (255, 0, 0),
            line_width : int = 2,
            ):
        
        self._drawing = False
        self._start_pos = (0,0)
        self._end_pos = (0,0)
        self._line_color = line_color
        self._line_width = line_width
        self._block_size = block_size
        self._distance_text = None

        self._font = pygame.font.Font(None, font_size)

    def draw(self, screen):
        if self._start_pos and self._end_pos:
            pygame.draw.line(screen, self._line_color, self._start_pos, self._end_pos, self._line_width)

        if self._distance_text:
            text_rect = self._distance_text.get_rect(center=self._midpoint)
            screen.blit(self._distance_text, text_rect)

    def update(self, event_pos):
        
        self._end_pos = event_pos
        self._distance = int(calculate_distance(self._start_pos, self._end_pos))
        self._midpoint = ((self._start_pos[0] + self._end_pos[0]) // 2, (self._start_pos[1] + self._end_pos[1]) // 2)
        self._distance_text = self._font.render(str(round(self._distance / self._block_size)) + " blocks", True, self._line_color)

    @property
    def start_pos(self):
        return self._start_pos
    
    @start_pos.setter
    def start_pos(self, value):
        self._start_pos = value

    @property
    def end_pos(self):
        return self._end_pos
    
    @end_pos.setter
    def end_pos(self, value):
        self._end_pos = value

    @property
    def drawing(self):
        return self._drawing
    
    @drawing.setter
    def drawing(self, value):
        self._drawing = value

class ShowPathFinder:

    _pathfinder : PathFinder
    _pathscene : PathScene
    _path_way : PathWay

    _tiles_grid : list[list[Tile]]
    _grid_height : int
    _grid_width : int

    _font : pygame.font.Font

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

        self._font_size = 24
        self._font = pygame.font.Font(None, self._font_size)
            

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
        tile_coord_x, tile_coord_y = self._get_mouse_tile_coords()

        pygame.draw.rect(
            self._screen, 
            (50, 50, 50), (
                tile_coord_x * self._block_size, 
                tile_coord_y * self._block_size, 
                self._block_size, 
                self._block_size)
        )

    def _get_mouse_grid_tile_coords(self):
        '''Get mouse position in relation to the grid (The Y is vertically inverted)'''
            
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tile_coord_x = int(mouse_x / self._block_size)
        tile_coord_y = abs(int(mouse_y / self._block_size) - self._grid_height) - 1

        return tile_coord_x, tile_coord_y
    
    def _get_mouse_tile_coords(self):
        '''Get mouse position in relation to the grid with window coordinates'''

        mouse_x, mouse_y = pygame.mouse.get_pos()
        tile_coord_x = int(mouse_x / self._block_size)
        tile_coord_y = (int(mouse_y / self._block_size))

        return tile_coord_x, tile_coord_y

    def _draw_cursor_text(self):

        mouse_x, mouse_y = pygame.mouse.get_pos()

        tile_coord_x, tile_coord_y = self._get_mouse_grid_tile_coords()

        text_surface = self._font.render(f"({tile_coord_x}, {tile_coord_y})", True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.center = (mouse_x, mouse_y)

        self._screen.blit(text_surface, text_rect)

    def _get_grid_coords_to_window_coords(self, x, y):
        return x * self._block_size, abs(y * self._block_size - self._window_height) - 1
    
    def _get_window_coords_to_grid_coords(self, x, y):
        return int(x / self._block_size), abs(int(y / self._block_size) - self._grid_height) - 1

    def _draw_path_points(self):

        last_point = None
        node_count = 0

        for point in self._pathfinder.path_points:
            if not last_point:
                last_point = self._get_grid_coords_to_window_coords(point.x, point.y)
                last_point = (
                    last_point[0] + self._block_size / 2, 
                    last_point[1] - self._block_size / 2) # center the point
                continue

            current_point = self._get_grid_coords_to_window_coords(point.x, point.y)
            current_point = (
                current_point[0] + self._block_size / 2, 
                current_point[1] - self._block_size / 2)

            pygame.draw.line(
                self._screen, 
                (255, 255, 255), 
                last_point,
                current_point,
                5
            )

            
            last_point = current_point

            #draw node count test on the last point
            text_surface = self._font.render(str(node_count), True, (255, 0, 0))
            text_rect = text_surface.get_rect()
            text_rect.center = last_point[0] - 20, last_point[1] - 20
            self._screen.blit(text_surface, text_rect)

            node_count += 1

    def show(self):

        line_measure = LineMeasure(block_size=self._block_size)
        
        # Main game loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # Draw line event
                elif event.type == pygame.MOUSEBUTTONDOWN:

                    # middle mouse
                    if event.button == 2:
                        line_measure.drawing = True
                        line_measure.start_pos = event.pos
                        line_measure.end_pos = event.pos

                    if event.button == 1:
                        self._pathfinder.set_origin(*self._get_mouse_grid_tile_coords())
                        self._pathfinder.update_path()

                    if event.button == 3:
                        self._pathfinder.set_target(*self._get_mouse_grid_tile_coords())
                        self._pathfinder.update_path()
                        
                elif event.type == pygame.MOUSEMOTION:
                    if line_measure.drawing:
                        line_measure.end_pos = event.pos

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 2:  # Left mouse button released
                        line_measure.drawing = False
            
                if line_measure.drawing:
                    line_measure.update(event.pos)

            self._screen.fill((0, 0, 0))

            self._draw_grid(self._tiles_grid)
            self._draw_grid(self._path_way.grid(horizontal=True))

            self._draw_grid_lines()
            self._draw_cursor_text()
            self._draw_path_points()

            # Draw the line
            line_measure.draw(self._screen)
            pygame.display.flip()

        # Quit Pygame
        pygame.quit()
        sys.exit(0)