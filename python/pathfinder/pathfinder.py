
from enum import Enum

import random

from .grid import (
    LevelGrid,
    PathWay,
    PathScene,
    Tile
)
        
class PathFinder:

    _level : LevelGrid
    _pathscene : PathScene
    _path_way : PathWay

    _target : tuple[int, int]
    _origin : tuple[int, int]

    def __init__(self):
        self._target = (-1, -1)
        self._origin = (-1, -1)

        self._level = LevelGrid([])
        self._pathscene = PathScene([])
        self._path_way = PathWay([])


    def set_random_target(self):
        valid_positions = [(x,y) for x in range(len(self._path_way.grid())) for y in range(len(self._path_way.grid()[0])) if self._path_way.grid()[x][y] == Tile.EMPTY]
        x, y = random.choice(valid_positions)
        self._path_way.set(x, y, Tile.PATHTARGET)

    def set_origin(self, x, y):
        if self._origin:
            self._path_way.set(*self._origin, Tile.EMPTY)

        self._path_way.set(x, y, Tile.PATHORIGIN)
        self._origin = (x, y)

    def set_target(self, x, y):
        if self._target:
            self._path_way.set(*self._target, Tile.EMPTY)
        self._path_way.set(x, y, Tile.PATHTARGET)
        self._target = (x, y)

    def start_scene(self, grid_data):

        self._level = LevelGrid(grid_data)
        self._pathscene = PathScene(grid_data)
        self._path_way = PathWay(grid_data)

        self._pathscene.generate_floor_areas()
        self._pathscene.generate_corner_climb_areas()
        self._pathscene.generate_wall_climb_areas()
        self._pathscene.create_path_nodes()
       
    def display(self):
        
        print(self._level)
        print(self._pathscene)


