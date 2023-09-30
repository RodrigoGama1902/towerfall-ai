
from .base import Grid, Tile

class PathWay(Grid):

    def set_target(self, x, y):
        self.set(x, y, Tile.PATHTARGET)

    def set_origin(self, x, y):
        self.set(x, y, Tile.PATHORIGIN)

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