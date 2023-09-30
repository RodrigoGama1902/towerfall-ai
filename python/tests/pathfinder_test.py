import pytest

from pathfinder import PathFinder
from fixtures.test_levels.level1 import *
from pathfinder.grid import Tile

from pathfinder.show import ShowPathFinder

@pytest.fixture
def start_space():
    print("\n\n")

def test_simple_display(start_space):

    pathfinder = PathFinder()
    pathfinder.start_scene(LEVEL1)
    pathfinder.set_origin(*LEVEL1_ORIGIN)
    pathfinder.set_target(*LEVEL1_TARGET)

    display = ShowPathFinder(pathfinder)
    display.show()








