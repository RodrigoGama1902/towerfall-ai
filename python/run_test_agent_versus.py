from agents import SimpleAgent, TestAgent
from common.logging_options import default_logging
from towerfall import Towerfall

default_logging()

'''
Two agents playing a 1 versus 1 match.
'''

def main():
  # Creates or reuse a Towerfall game.
  towerfall = Towerfall(
    verbose = 1,
    config = dict(
      mode='versus',
      level='',
      fps=60,
      agentTimeout='00:00:02',
      agents=[
        dict(type='remote', archer='green-alt', team='blue'),
        dict(type='remote', archer='red-alt', team='red')],
    )
  )

  connections = []
  agents = []

  # add one SimpleAgent and one TestAgent
  connections.append(towerfall.join(timeout=10, verbose=0))
  agents.append(SimpleAgent(connections[0]))

  connections.append(towerfall.join(timeout=10, verbose=0))
  agents.append(TestAgent(connections[1]))


  while True:
    # Read the state of the game then replies with an action.
    for connection, agent in zip(connections, agents):
      game_state = connection.read_json()
      agent.act(game_state)


if __name__ == '__main__':
  main()