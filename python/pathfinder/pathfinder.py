
import random
import math

from .grid import (
    LevelGrid,
    PathWay,
    PathScene,
    Tile
)

from dataclasses import dataclass


@dataclass
class PathPoint:

    tile : Tile
    x : int
    y : int

    
        
class PathFinder:

    _level : LevelGrid
    _pathscene : PathScene
    _path_way : PathWay

    _target : tuple[int, int]
    _origin : tuple[int, int]

    _path_points : list[PathPoint]
    _path_ancors : list[tuple[int, int]]

    def __init__(self):
        self._target = (-1, -1)
        self._origin = (-1, -1)

        self._level = LevelGrid([])
        self._pathscene = PathScene([])
        self._path_way = PathWay([])
        
        self._path_points = []


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

    def is_clear_path(self, x1, y1, x2, y2):

        # Calculate the direction vector from the enemy to the player
        dx = x2 - x1
        dy = y2 - y1

        # Calculate the length of the direction vector
        length = math.sqrt(dx ** 2 + dy ** 2)

        # Normalize the direction vector
        if length == 0:
            return False

        dx /= length
        dy /= length

        # Initialize the ray's starting position
        x, y = x1, y1

        # Iterate along the ray from the enemy to the player
        while math.sqrt((x - x1) ** 2 + (y - y1) ** 2) < length:
            # Check if the current cell is an obstacle

            #round up
            cell_x = math.ceil(x)
            cell_y = math.ceil(y)

            if x < 0 or x >= len(self._level.grid()):
                return False
            if y < 0 or y >= len(self._level.grid()[0]):
                return False
            if self._level.grid()[cell_x][cell_y] == Tile.WALL: 
                return False  # There is a collision, not a clear path
            # Move the ray to the next cell
            x += dx
            y += dy

        # If the loop finishes, there is a clear path
        return True


    def _get_accessible_anchors(self, ignore_archor_points, current_anchor):

        near_anchors :  list[tuple[int, int]] = []

        for anchor in self._path_ancors:
            if anchor in ignore_archor_points:
                print("already in current anchor points: ", *anchor)
                continue
            if self._path_way.get_distance_between(*anchor, *current_anchor) > 10:
                print("anchor too far: ", *anchor)
                continue
            if not self.is_clear_path(*anchor, *current_anchor):
                print("no clear path to anchor: ", *anchor)
                continue

            near_anchors.append(anchor)
        
        return near_anchors

    def update_path(self):
        
        self._path_points = []
        self._path_points.append(PathPoint(Tile.PATHORIGIN, *self._origin))

        current_anchor : tuple[int, int] = self._origin
        current_anchor_points = []

        # use is_clear_path
        self.is_clear_path(*current_anchor, *self._target)

        # Loop until we reach the target or we run out of anchors
        while True and len(current_anchor_points) < len(self._path_ancors):
            print(f"> {len(current_anchor_points)} Current anchor: ", *current_anchor)

            distance_to_target = self._path_way.get_distance_between(*current_anchor, *self._target)
            if distance_to_target < 10 and self.is_clear_path(*current_anchor, *self._target):
                print("target reached")
                break

            available_anchors = self._get_accessible_anchors(current_anchor_points, current_anchor)

            print("near anchors: ", *available_anchors)
            # get closest anchor to target from the 3
            closest_valid_anchor = None
            for anchor in available_anchors:
                if not closest_valid_anchor:
                    closest_valid_anchor = anchor
                    continue
                
                print("> Checking next available anchors for: ", *anchor)
                next_available_anchors = self._get_accessible_anchors(available_anchors, anchor)
                if not next_available_anchors:
                    print("no next available anchors for: ", *anchor)
                    continue

                if self._path_way.get_distance_between(*closest_valid_anchor, *self._target) > self._path_way.get_distance_between(*anchor, *self._target):
                    closest_valid_anchor = anchor

            if closest_valid_anchor:
                current_anchor = closest_valid_anchor  
                current_anchor_points.append(closest_valid_anchor)
            else:
                print("no valid anchor")
                break

        self._path_points.extend([PathPoint(Tile.PATHUP, *anchor) for anchor in current_anchor_points])
        self._path_points.append(PathPoint(Tile.PATHTARGET, *self._target))

    @property
    def path_points(self):
        return self._path_points

    def start_scene(self, grid_data):

        self._level = LevelGrid(grid_data)
        self._pathscene = PathScene(grid_data)
        self._path_way = PathWay(grid_data)

        self._pathscene.generate_floor_areas()
        self._pathscene.generate_corner_climb_areas()
        self._pathscene.generate_wall_climb_areas()

        self._path_ancors = self._pathscene.get_path_ancors()

    def display(self):
        
        print(self._level)
        print(self._pathscene)


