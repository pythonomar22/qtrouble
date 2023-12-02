import random
import numpy as np
import pickle
from tqdm import tqdm
from game import TroubleGameBasic
from hyperopt import hp, fmin, tpe, Trials, STATUS_OK

random.seed("cs221")

space = {
    'move_out_home': hp.uniform('move_out_home', -100, 0),
    'move_on_board': hp.uniform('move_on_board', -100, 0),
    'complete_lap': hp.uniform('complete_lap', -100000, 0),
    'capture_opponent': hp.uniform('capture_opponent', -10000, 0),
    'risk_change': hp.uniform('risk_change', -100, 0),
    'no_move_penalty': hp.uniform('no_move_penalty', -100, 0),
}

def objective(weights):
    agent = QLearningAgent(weights=weights, agent_player='Red')
    agent.train(num_episodes=50, agent_player='Red')
    average_performance = agent.calculate_performance(num_eval_games=100)
    return {'loss': -average_performance, 'status': STATUS_OK}



class QLearningAgent:
    def __init__(self, *weights, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.1, agent_player='Red'):
        self.weights = weights
        self.learning_rate = learning_rate  # Alpha
        self.discount_factor = discount_factor  # Gamma
        self.exploration_rate = exploration_rate  # Epsilon
        self.q_table = {}  # Initialize Q-table
        self.agent_player = agent_player

    def get_state(self, game):
        # Convert the game state to a tuple that represents the current state
        state = (tuple(game.board), tuple(tuple(game.pawns[player]['Home']) for player in game.players),
                 tuple(tuple(game.pawns[player]['Board']) for player in game.players),
                 tuple(tuple(game.pawns[player]['Finished']) for player in game.players))
        return state

    def choose_action(self, state, possible_actions):
        if not possible_actions:
            return None

        # Ensure the current state is in the Q-table with all possible actions
        if state not in self.q_table or not self.q_table[state]:
            self.q_table[state] = {action: 0.0 for action in possible_actions}

        if random.uniform(0, 1) < self.exploration_rate:
            # Exploration: choose a random action
            return random.choice(possible_actions)
        else:
            # Exploitation: choose the best action based on current Q-values
            return max(self.q_table[state], key=self.q_table[state].get, default=None)



    def learn(self, state, action, reward, next_state, possible_actions, possible_next_actions):
        # Initialize or update the Q-table for the current state
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in possible_actions}
        elif action not in self.q_table[state]:
            self.q_table[state][action] = 0.0

        # Initialize the Q-table for the next state
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0.0 for a in possible_next_actions}

        max_q_value_next_state = max(self.q_table[next_state].values(), default=0)

        # Update Q-table
        self.q_table[state][action] += self.learning_rate * (reward + self.discount_factor * max_q_value_next_state - self.q_table[state][action])



    def train(self, num_episodes, agent_player='Red'):
        for episode in tqdm(range(num_episodes), desc="Training Progress"):
            game = TroubleGameBasic()
            state = self.get_state(game)

            while not game.check_winner():
                possible_actions, dice_roll = game.get_possible_actions(agent_player)
                action = self.choose_action(state, possible_actions)
                if action is None:
                    continue
                reward, next_state = game.perform_action(agent_player, action, dice_roll)
                possible_next_actions, _ = game.get_possible_actions(agent_player)
                self.learn(state, action, reward, next_state, possible_actions, possible_next_actions)
                state = next_state

            # Evaluate performance after each episode
            #win_rate = self.calculate_performance(num_eval_games=100)
            #print(f"Episode {episode + 1}/{num_episodes}: Win Rate = {win_rate * 100:.2f}%")

    def load_q_table(self, file_path):
        with open(file_path, 'rb') as file:
            self.q_table = pickle.load(file)

# best_weights = fmin(fn=objective, space=space, algo=tpe.suggest, max_evals=1, trials=Trials())
# print("Best weights found:", best_weights)

# agent = QLearningAgent()
# agent.train(num_episodes=1000, agent_player='Red')  # Train the agent

# with open('q_table.pkl', 'wb') as file:
#     pickle.dump(agent.q_table, file)

# Initialize the agent
agent = QLearningAgent(agent_player='Red')

# Load the pre-trained Q-table
q_table_path = "C:/Users/omara/OneDrive/Desktop/cs221/q_table400wins.pkl"
agent.load_q_table(q_table_path)
print("hello")

# Evaluation loop
num_games = 1000
overall_statistics = {}

for _ in tqdm(range(num_games), desc="Evaluation Progress"):
    game = TroubleGameBasic()
    game.game_statistics = overall_statistics

    turn_count = 0
    while not game.check_winner():
        current_player = game.players[turn_count % len(game.players)]
        turn_count += 1

        if current_player == agent.agent_player:
            state = agent.get_state(game)
            possible_actions, dice_roll = game.get_possible_actions(current_player)
            action = agent.choose_action(state, possible_actions)
            if action is not None:
                reward, next_state = game.perform_action(current_player, action, dice_roll)
        else:
            game.take_turn(current_player, random.randint(1, 6))

        winner = game.check_winner()
        if winner:
            game.record_statistics(winner, turn_count)
            break

# Print overall statistics
print("Agent's Overall Statistics:")
for player, stats in overall_statistics.items():
    if stats['wins'] > 0:
        avg_turns = stats['total_turns'] / stats['wins']
        print(f"{player}: Wins - {stats['wins']}, Average Turns to Win - {avg_turns:.2f}")
