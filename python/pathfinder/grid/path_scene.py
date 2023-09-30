
from .base import Grid, Tile
        
class PathScene(Grid):

    def _get_tiles(self, grid_data):

        tiles : list[list[Tile]] = []
        for i in range(len(grid_data)):
            tiles.append([])
            for j in range(len(grid_data[0])):

                match str(grid_data[i][j]):
                    case "0":
                        tiles[i].append(Tile.EMPTY)
                    case "1":
                        tiles[i].append(Tile.WALL)

        return tiles
    
    def generate_floor_areas(self):

        for i in range(len(self._grid)):
            for j in range(len(self._grid[0])):
                if self._grid[i][j] == Tile.WALL:
                    tile_left = self.get_tile_above(i, j)
                    if tile_left == Tile.EMPTY:
                        self.set(i, j, Tile.PATHFLOOR)

    def generate_wall_climb_areas(self):

        for i in range(len(self._grid)):
            for j in range(len(self._grid[0])):
                if self._grid[i][j] == Tile.WALL:
                    tile_left = self.get_tile_left(i, j)
                    if tile_left == Tile.EMPTY:
                        self.set(i, j, Tile.PATHWALL)
                        continue
                    tile_right = self.get_tile_right(i, j)
                    if tile_right == Tile.EMPTY:
                        self.set(i, j, Tile.PATHWALL)
                        continue

    def generate_corner_climb_areas(self):

        for i in range(len(self._grid)):
            for j in range(len(self._grid[0])):
                if self._grid[i][j] == Tile.PATHFLOOR:
                    tile_left = self.get_tile_left(i, j)
                    if tile_left == Tile.EMPTY:
                        self.set(i, j, Tile.PATHCORNER)
                        continue
                    tile_right = self.get_tile_right(i, j)
                    if tile_right == Tile.EMPTY:
                        self.set(i, j, Tile.PATHCORNER)
                        continue

    def create_path_nodes(self):

        for i in range(len(self._grid)):
            for j in range(len(self._grid[0])):
                if self._grid[i][j] in (Tile.PATHFLOOR, Tile.PATHCORNER):
                    self.set(i, j + 1, Tile.PATHNODE)
