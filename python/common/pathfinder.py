
from enum import Enum

import random

class Tile(Enum):

    EMPTY = '  '
    WALL = '\u2588\u2588'
    PATHORIGIN = 'OO'
    PATHTARGET = 'XX'
    PATHFLOOR = '\u2593\u2593'
    PATHWALL = '\u2591\u2591'
    PATHCORNER = '\u2592\u2592'
    PATHUP = 2
    PATHDOWN = 3
    PATHLEFT = 4
    PATHRIGHT = 5

class Grid:

    _tiles : list[list[Tile]]

    def __init__(self, grid_data):

        self._grid_data = grid_data
        self._tiles = self._get_tiles(grid_data)

    def set_tile(self, x, y, tile):
        self._tiles[x][y] = tile

    @staticmethod
    def _get_tiles(grid_data):

        tiles : list[list[Tile]] = []
        for i in range(len(grid_data)):
            tiles.append([])
            for j in range(len(grid_data[0])):
                match grid_data[i][j]:
                    case 0:
                        tiles[i].append(Tile.EMPTY)
                    case 1:
                        tiles[i].append(Tile.WALL)
        return tiles
        
    def __eq__(self, __value: object) -> bool:
        return self._grid_data == __value._grid_data

    def __repr__(self) -> str:
        string = ""

        height = len(self._tiles[0])
        width = len(self._tiles)

        current_height = height - 1

        for i in range(height):
            for j in range(width):
                string += self._tiles[j][current_height].value

            string += "\n"
            current_height -= 1

        return string
    
    def _is_in_bounds(self, x, y):
        return x >= 0 and y >= 0 and x < len(self._tiles) and y < len(self._tiles[0])
    
    def get_tile_left(self, x, y):
        new_x = x - 1
        if not self._is_in_bounds(new_x, y):
            return None
        return self._tiles[new_x][y]
    
    def get_tile_right(self, x, y):
        new_x = x + 1
        if not self._is_in_bounds(new_x, y):
            return None
        return self._tiles[new_x][y]
    
    def get_tile_below(self, x, y):
        new_y = y - 1
        if not self._is_in_bounds(x, new_y):
            return None
        return self._tiles[x][y-1]
    
    def get_tile_above(self, x, y):
        new_y = y + 1
        if not self._is_in_bounds(x, new_y):
            return None
        return self._tiles[x][y+1]

class PathFinder:

    _grid : Grid = None

    _last_target_position : tuple[int, int] = None
    _last_origin_position : tuple[int, int] = None

    last_displayed_grid : Grid = None

    def __init__(self):
        pass

    def set_random_target(self):
        valid_positions = [(x,y) for x in range(len(self._grid._tiles)) for y in range(len(self._grid._tiles[0])) if self._grid._tiles[x][y] == Tile.EMPTY]
        x, y = random.choice(valid_positions)
        self.set_target(x, y)

    def set_origin(self, x, y):
        if self._last_origin_position:
            self._grid.set_tile(*self._last_origin_position, Tile.EMPTY)
        self._grid.set_tile(x, y, Tile.PATHORIGIN)
        self._last_origin_position = (x, y)

    def set_target(self, x, y):
        if self._last_target_position:
            self._grid.set_tile(*self._last_target_position, Tile.EMPTY)
        self._grid.set_tile(x, y, Tile.PATHTARGET)
        self._last_target_position = (x, y)

    def _generate_floor_areas(self):

        for i in range(len(self._grid._tiles)):
            for j in range(len(self._grid._tiles[0])):
                if self._grid._tiles[i][j] == Tile.WALL:
                    tile_left = self._grid.get_tile_above(i, j)
                    if tile_left == Tile.EMPTY:
                        self._grid.set_tile(i, j, Tile.PATHFLOOR)

    def _generate_wall_climb_areas(self):

        for i in range(len(self._grid._tiles)):
            for j in range(len(self._grid._tiles[0])):
                if self._grid._tiles[i][j] == Tile.WALL:
                    tile_left = self._grid.get_tile_left(i, j)
                    if tile_left == Tile.EMPTY:
                        self._grid.set_tile(i, j, Tile.PATHWALL)
                        continue
                    tile_right = self._grid.get_tile_right(i, j)
                    if tile_right == Tile.EMPTY:
                        self._grid.set_tile(i, j, Tile.PATHWALL)
                        continue

    def _generate_corner_climb_areas(self):

        for i in range(len(self._grid._tiles)):
            for j in range(len(self._grid._tiles[0])):
                if self._grid._tiles[i][j] == Tile.PATHFLOOR:
                    tile_left = self._grid.get_tile_left(i, j)
                    if tile_left == Tile.EMPTY:
                        self._grid.set_tile(i, j, Tile.PATHCORNER)
                        continue
                    tile_right = self._grid.get_tile_right(i, j)
                    if tile_right == Tile.EMPTY:
                        self._grid.set_tile(i, j, Tile.PATHCORNER)
                        continue

                    
    def update_grid(self, grid_data):
        self._grid = Grid(grid_data)

        self._generate_floor_areas()
        self._generate_corner_climb_areas()
        self._generate_wall_climb_areas()

    def display(self):

        if not self.last_displayed_grid or (not self._grid == self.last_displayed_grid):
            print(self._grid)
            self.last_displayed_grid = self._grid
