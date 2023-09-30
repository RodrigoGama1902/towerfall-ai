
from enum import Enum
from dataclasses import dataclass

from abc import ABC, abstractmethod

@dataclass
class BlockRepr:

    text : str
    color : tuple[int, int, int]

class Tile(Enum):

    EMPTY = BlockRepr('  ', (0, 0, 0))
    WALL = BlockRepr('\u2588\u2588', (171, 171, 171))

    PATHORIGIN = BlockRepr('OO', (0, 255, 0))
    PATHTARGET = BlockRepr('XX', (255, 0, 0))

    PATHNODE = BlockRepr("[]",(255, 255, 255))

    PATHUP = BlockRepr("^^",(255, 255, 255))
    PATHDOWN = BlockRepr("vv",(255, 255, 255))
    PATHLEFT = BlockRepr("<<",(255, 255, 255))
    PATHRIGHT = BlockRepr(">>",(255, 255, 255))
    PATHPASSED = BlockRepr("##",(255, 255, 255))

    PATHFLOOR = BlockRepr('\u2593\u2593', (31, 207, 0))
    PATHWALL = BlockRepr('\u2591\u2591', (69, 141, 230))
    PATHCORNER = BlockRepr('\u2592\u2592', (140, 155, 239))

@dataclass
class Grid(ABC):

    _grid : list[list[Tile]]

    def __init__(self, grid : list[list[str]]):
        self._grid = self._get_tiles(grid)

    @abstractmethod
    def _get_tiles(self, grid_data : list[list[str]]) -> list[list[Tile]]:
        ...
    
    def _is_in_bounds(self, x, y):
        return x >= 0 and y >= 0 and x < len(self._grid) and y < len(self._grid[0])
    
    def get_tile_left(self, x, y):
        new_x = x - 1
        if not self._is_in_bounds(new_x, y):
            return None
        return self._grid[new_x][y]
    
    def get_tile_right(self, x, y):
        new_x = x + 1
        if not self._is_in_bounds(new_x, y):
            return None
        return self._grid[new_x][y]
    
    def get_tile_below(self, x, y):
        new_y = y - 1
        if not self._is_in_bounds(x, new_y):
            return None
        return self._grid[x][y-1]
    
    def get_tile_above(self, x, y):
        new_y = y + 1
        if not self._is_in_bounds(x, new_y):
            return None
        return self._grid[x][y+1]
    
    def get_distance_between(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)


    def _tiles_horizontal(self):

        tiles_horizontal : list[list[Tile]] = []

        height = len(self._grid[0])
        width = len(self._grid)

        current_height = height - 1

        for i in range(height):
            tiles_horizontal.append([])
            for j in range(width):
                tiles_horizontal[i].append(self._grid[j][current_height])

            current_height -= 1

        return tiles_horizontal
    

    def grid(self, horizontal = False):
        if horizontal:
            return self._tiles_horizontal()
        return self._grid
    
    def get(self, x, y):
        return self._grid[x][y]
    
    def set(self, x, y, tile):
        self._grid[x][y] = tile

    def __repr__(self) -> str:
        string = ""

        height = len(self._grid[0])
        width = len(self._grid)

        current_height = height - 1

        for i in range(height):
            for j in range(width):
                tile_repr : BlockRepr = self._grid[j][current_height].value
                string += tile_repr.text

            string += "\n"
            current_height -= 1

        return string