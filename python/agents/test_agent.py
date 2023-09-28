import logging
import random
import math

from pprint import pprint

from typing import Any, Mapping

from towerfall import Connection

from common.utils import (
    get_distance_from_point,
)

from common.pathfinder import PathFinder

class TestAgent:
  '''
  A minimal implementation of an agent that shows how to communicate with the game.
  It can be used in modes:
    - quest
    - versus
    - sandbox

  params connection: A connection to a Towerfall game.
  params attack_archers: If True, the agent will attack other neutral archers.
  '''

  pathfinder : PathFinder

  def __init__(self, connection: Connection, attack_archers: bool = False):
    self.state_init: Mapping[str, Any] = {}
    self.state_scenario: Mapping[str, Any] = {}
    self.state_update: Mapping[str, Any] = {}
    self.pressed = set()
    self.connection = connection
    self.attack_archers = attack_archers

    self.last_action = None
    self.pathfinder = PathFinder()

  def _log_action(self, action : str):

    if action != self.last_action:
      logging.info(action)
      self.last_action = action

  def act(self, game_state: Mapping[str, Any]):
    '''
    Handles a game message.
    '''

    # There are three main types to handle, 'init', 'scenario' and 'update'.
    # Check 'type' to handle each accordingly.
    if game_state['type'] == 'init':
      # 'init' is sent every time a match series starts. It contains information about the players and teams.
      # The seed is based on the bot index so each bots acts differently.
      self.state_init = game_state
      random.seed(self.state_init['index'])
      # Acknowledge the init message.
      self.connection.send_json(dict(type='result', success=True))
      return True

    if game_state['type'] == 'scenario':
      # 'scenario' informs your bot about the current state of the ground. Store this information
      # to use in all subsequent loops. (This example bot doesn't use the shape of the scenario)
      self.state_scenario = game_state
      self.pathfinder.update_grid(game_state['grid'])
      # Acknowledge the scenario message.
      self.connection.send_json(dict(type='result', success=True))
      return

    if game_state['type'] == 'update':
      # 'update' informs the state of entities in the map (players, arrows, enemies, etc).
      self.state_update = game_state

    # After receiving an 'update', your bot is expected to output string with the pressed buttons.
    # Each button is represented by a character:
    # r = right
    # l = left
    # u = up
    # d = down
    # j = jump
    # z = dash
    # s = shoot
    # The order of the characters are irrelevant. Any other character is ignored. Repeated characters are ignored.

    # This bot acts based on the position of the other player only. It
    # has a very random playstyle:
    #  - Runs to the enemy when they are below.
    #  - Runs away from the enemy when they are above.
    #  - Shoots when in the same horizontal line.
    #  - Dashes randomly.
    #  - Jumps randomly.

    my_state = None
    enemy_state = None

    players = []
    arrows = []


    for state in self.state_update['entities']:

      if state['type'] == 'arrow':
        arrows.append(state)

      if state['type'] == 'archer':
        players.append(state)
        if state['playerIndex'] == self.state_init['index']:
          my_state = state

    # If the agent is not present, it means it is dead.
    if my_state == None:
      self._log_action('dead')
      # You are required to reply with actions, or the agent will get disconnected.
      self.send_actions()
      return

    # Try to find an enemy archer.
    for state in players:
      if state['playerIndex'] == my_state['playerIndex']:
        continue
      if (self.attack_archers and state['team'] == 'neutral') or state['team'] != my_state['team']:
        enemy_state = state
        break

    # If no enemy archer is found, try to find another enemy.
    if not enemy_state:
      for state in self.state_update['entities']:
        if state['isEnemy']:
          enemy_state = state

    # If no enemy is found, means all are dead.
    if enemy_state == None:
      self.send_actions()
      return
    
    self.my_state = my_state
    self.my_pos = my_state['pos']

    enemy_pos = enemy_state['pos']
    enemy_distance = self._get_distance_to(enemy_pos['x'], enemy_pos['y'])

    self.pathfinder.update_grid(self.state_scenario['grid'])
    self.pathfinder.set_target(int(enemy_pos['x'] / self.state_scenario['cellSize']), int(enemy_pos['y'] / self.state_scenario['cellSize']))
    self.pathfinder.set_origin(int(self.my_pos['x'] / self.state_scenario['cellSize']), int(self.my_pos['y'] / self.state_scenario['cellSize']))
    self.pathfinder.display()

    return self.send_actions()
    
    if not my_state["arrows"]:
      if enemy_distance < 30 and enemy_pos['y'] >= self.my_pos['y'] + 10 and self._is_heading_towards_me(
        enemy_pos['x'], 
        enemy_pos['y'], 
        enemy_state['vel']['x'], 
        enemy_state['vel']['y']): 
      
        self._log_action('fleeing from enemy jump, no arrows')
        self._flee_from_point(enemy_pos['x'], enemy_pos['y'], allow_vertical= False, use_dash= True)
        return self.send_actions()
     
    # Defend against shooting arrows
    for arrow in arrows:
      
      if arrow["state"] == "shooting" or arrow["state"] == "gravity":     
        if not self._is_heading_towards_me(
          arrow['pos']['x'], 
          arrow['pos']['y'], 
          arrow['vel']['x'], 
          arrow['vel']['y']):
          continue


        arrow_distance = self._get_distance_to(arrow['pos']['x'], arrow['pos']['y'])
        if arrow_distance > 25 and arrow_distance < 80 and my_state["arrows"]: 
            self._log_action('shooting towards arrow')
            self._go_towards_point(arrow['pos']['x'], arrow['pos']['y'], use_dash= False)
            self._shoot(fail_chance=15)
            return self.send_actions()
        
        if arrow_distance < 25:
          if not my_state["state"] in ("dodging", "ledgeGrab"):
            self._log_action('dodging towards arrow')
            self._go_towards_point(arrow['pos']['x'], arrow['pos']['y'], use_dash= True)

          if arrow["arrowType"] == "bomb" and self._get_distance_to(arrow['pos']['x'], arrow['pos']['y']) > 20:
            self._log_action('fleeing from shooting bomb arrow')
            self._flee_from_point(arrow['pos']['x'], arrow['pos']['y'], use_dash= True)
            return self.send_actions()
      
      if arrow["state"] == "stuck":
        if arrow["arrowType"] == "bomb":
          if self._get_distance_to(arrow['pos']['x'], arrow['pos']['y']) > 20:
            self._log_action('fleeing from stuck bomb arrow')
            self._flee_from_point(arrow['pos']['x'], arrow['pos']['y'], use_dash= True)
            return self.send_actions()
          else:
            self._log_action('dashing towards stuck bomb arrow')
            self._go_towards_point(arrow['pos']['x'], arrow['pos']['y'], use_dash= True)
            return self.send_actions()
             

    if my_state["arrows"]:
      self._log_action('going towards enemy')
      self._go_towards_point(enemy_pos['x'], enemy_pos['y'], allow_vertical= False)

      if enemy_distance < 100:
        if self.is_clear_path(enemy_pos['x'], enemy_pos['y']):
          self._shoot()
        else:
          self._log_action('blocked')

    else:
      closest_stuck_arrow = self._find_closest_available_arrow(arrows)
      if closest_stuck_arrow:
        self._log_action('no arrows left, going towards stuck arrow')
        self._go_towards_point(closest_stuck_arrow['pos']['x'], closest_stuck_arrow['pos']['y'], use_dash= False)
      else:
        self._log_action('no arrows left, fleeing from enemy')
        self._flee_from_point(enemy_pos['x'], enemy_pos['y'])

    # Randomly jumps
    if random.randint(0, 19) == 0:
      self._log_action('random jumping')
      self.press('j')

    return self.send_actions()
  
  def _is_heading_towards_me(self, target_x, target_y, vel_x, vel_y) -> bool:
     
    target_to_my_pos = (self.my_pos['x'] - target_x, self.my_pos['y'] - target_y)
    dot_product = target_to_my_pos[0] * vel_x + target_to_my_pos[1] * vel_y

    return dot_product > 0

  def _get_distance_to(self, target_x, target_y):

    my_pos_x = self.my_pos['x']
    my_pos_y = self.my_pos['y']

    return get_distance_from_point(my_pos_x, my_pos_y, target_x, target_y)
  
  def _get_snap_direction_angle_to(self, target_x, target_y):
     
    dx = target_x - self.my_pos['x']
    dy = self.my_pos['y']- target_y

    angle = math.atan2(dy, dx)
    angle_degrees = math.degrees(angle)

    possible_snap_values = [0, 45, -45, 90, -90, 135, -135, 180]
    snap_value_angle = min(possible_snap_values, key=lambda x:abs(x-angle_degrees))

    return snap_value_angle
   
  def _go_towards_point(
      self, 
      target_x, 
      target_y, 
      allow_vertical = True, 
      use_dash = False):

      snap_value_angle = self._get_snap_direction_angle_to(target_x, target_y)

      key_presses = {
        0 : ['r'],
        45 : ['r', 'd'],
        -45 : ['r', 'u'],
        90 : ['d'],
        -90 : ['u'],
        135 : ['l', 'd'],
        -135 : ['l', 'u'],
        180 : ['l']
      }

      if not allow_vertical:
        key_presses.update({
            -90: ['r'],
            90: ['l']
        })

      directions = key_presses.get(snap_value_angle, [])
      for direction in directions:
          self.press(direction)
      
      if use_dash:
        if random.randint(0, 1) == 0:
          self.press('z')

  def _flee_from_point(
      self, 
      target_x, target_y, allow_vertical = True, use_dash = False):

      snap_value_angle = self._get_snap_direction_angle_to(target_x, target_y)

      key_presses = {
        0: ['l'],
        45: ['l', 'u'],
        -45: ['l', 'd'],
        90: ['d'],
        -90: ['u'],
        135: ['r', 'd'],
        -135: ['r', 'u'],
        180: ['r']
      }

      if not allow_vertical:
        key_presses.update({
            -90: ['r'],
            90: ['l']
        })

      directions = key_presses.get(snap_value_angle, [])
      for direction in directions:
          self.press(direction)

      if use_dash:
        self.press('z')
      
  def _find_closest_available_arrow(self, arrows):

      for arrow in arrows:

          if arrow["state"] == "shooting" or arrow["state"] == "gravity":  
              continue

          arrow_x_distance = abs(arrow['pos']['x'] - self.my_pos['x'])
          arrow_y_distance = abs(arrow['pos']['y'] - self.my_pos['y'])

          if arrow_y_distance > 60:
              continue

          arrow_distance = math.sqrt(arrow_x_distance ** 2 + arrow_y_distance ** 2)

          if arrow_distance < 100:
              return arrow

  def is_clear_path(self, target_x, target_y):

    cellSize = self.state_scenario['cellSize'] # used to convert from world coordinates to grid coordinates
    scenario_grid = self.state_scenario['grid']

    x1, y1 = int(self.my_pos['x'] / cellSize), int(self.my_pos['y'] / cellSize) +1 # +1 to consider one block to keep head height
    x2, y2 = int(target_x / cellSize), int(target_y / cellSize) +1 

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

        if x < 0 or x >= len(scenario_grid):
            return False
        if y < 0 or y >= len(scenario_grid[0]):
            return False
        if scenario_grid[int(x)][int(y)] == 1:
            return False  # There is a collision, not a clear path
        # Move the ray to the next cell
        x += dx
        y += dy

    # If the loop finishes, there is a clear path
    return True

  def _shoot(self, fail_chance = 3):
    if self.my_state["arrows"]:
      self._log_action('shooting')
      if random.randint(0, fail_chance) == 0:
        self.press('s')
      else:
        self._log_action("failed to shoot")
    else:
      self._log_action('could not shoot, no arrows left')

  def press(self, b):
    self.pressed.add(b)

  def send_actions(self):
    assert self.state_update
    self.connection.send_json(dict(
      type = 'actions',
      actions = ''.join(self.pressed),
      id = self.state_update['id']
    ))
    self.pressed.clear()
