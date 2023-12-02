import random
from colorDisplay import print_game_board, colors, colorPrint
# random.seed("cs221")

class TroubleGameBasic:
    def __init__(self):
        # Initialize the game board with 28 spaces
        self.board = [None] * 28  
        # Define players and their pawns
        self.players = ['Red', 'Blue', 'Green', 'Yellow']
        # Each player has 4 pawns, initially at home, with identifiers like 'R0', 'B1', etc.
        self.pawns = {player: {'Home': [f"{player[0]}{i}" for i in range(4)], 
                               'Board': [], 
                               'Finished': []} 
                      for player in self.players}
        # Define start positions for each player
        self.start_positions = {'Red': 0, 'Blue': 7, 'Green': 14, 'Yellow': 21}

    def record_statistics(self, winner, turn_count):
        if winner not in self.game_statistics:
            self.game_statistics[winner] = {'wins': 0, 'total_turns': 0}
        self.game_statistics[winner]['wins'] += 1
        self.game_statistics[winner]['total_turns'] += turn_count


    def is_valid_move(self, player, pawn_id, new_position):
        for other_pawn_id in self.pawns[player]['Board']:
            if other_pawn_id != pawn_id and self.board[new_position] == other_pawn_id:
                return False  # Invalid move, space already occupied by another of player's pieces
        return True  # Move is valid

    def move_pawn(self, player, pawn_id, steps):
        if pawn_id in self.pawns[player]['Home']:
            if steps == 6:
                new_position = self.start_positions[player]
                if self.is_valid_move(player, pawn_id, new_position):
                    self.handle_collision(player, new_position)
                    self.pawns[player]['Home'].remove(pawn_id)
                    self.pawns[player]['Board'].append(pawn_id)
                    self.board[new_position] = pawn_id
        else:
            if pawn_id in self.pawns[player]['Board']:
                current_position = self.board.index(pawn_id)
                new_position = (current_position + steps) % 28
                if new_position != current_position and self.is_valid_move(player, pawn_id, new_position):
                    self.handle_collision(player, new_position)
                    self.board[current_position] = None
                    self.board[new_position] = pawn_id
                    # Check if pawn completed a lap and move to 'Finished' if true
                    if new_position == self.start_positions[player]:
                        self.pawns[player]['Board'].remove(pawn_id)
                        self.pawns[player]['Finished'].append(pawn_id)
                        self.board[new_position] = None

        #self.display_board()

    def handle_collision(self, player, position):
        if self.board[position] and self.board[position][0] != player[0]:
            collided_pawn_id = self.board[position]
            collided_player_initial = collided_pawn_id[0]
            
            # Map the initial letter back to the full name of the player
            player_mapping = {'R': 'Red', 'B': 'Blue', 'G': 'Green', 'Y': 'Yellow'}
            collided_player = player_mapping[collided_player_initial]

            self.pawns[collided_player]['Board'].remove(collided_pawn_id)
            self.pawns[collided_player]['Home'].append(collided_pawn_id)
            self.board[position] = None  # Clear the position on the board


    def display_board(self):
        # board_representation = ['--' if not pawn else pawn for pawn in self.board]
        # print_game_board(board_representation)
        board_representation = ['--' if not pawn else pawn for pawn in self.board]
        print(" ".join(board_representation))
        for player, data in self.pawns.items():
            print(f"{player}: Home - {data['Home']}, Board - {data['Board']}, Finished - {data['Finished']}")

    def play_game(self):
        turn_count = 0
        while True:
            for player in self.players:
                turn_count += 1
                dice_roll = random.randint(1, 6)
                self.take_turn(player, dice_roll)

                winner = self.check_winner()
                if winner:
                    self.record_statistics(winner, turn_count)
                    #print(f"{winner} wins the game in {turn_count} turns!")
                    return winner, turn_count


    def take_turn(self, player, dice_roll):
        if len(self.pawns[player]['Home']) > 0 and dice_roll == 6:
            pawn_id = self.pawns[player]['Home'][0]  # Pawn ready to move out
        elif len(self.pawns[player]['Board']) > 0:
            pawn_id = self.pawns[player]['Board'][0]  # First pawn on the board
        else:
            return  # No move possible

        self.move_pawn(player, pawn_id, dice_roll)  
        #print(f"{player} moved {pawn_id} this many spaces: {dice_roll}")

    def check_winner(self):
        """
        Check if any player has won the game.
        """
        for player, data in self.pawns.items():
            if len(data['Finished']) == 4:  # All pawns have finished
                return player
        return None
    
    def get_possible_actions(self, player):
        # Actions are pawns that can be moved
        possible_actions = []
        dice_roll = random.randint(1, 6)  # Simulate a dice roll

        if dice_roll == 6:  # Can move a pawn from home or any pawn on the board
            possible_actions.extend(self.pawns[player]['Home'])
            possible_actions.extend(self.pawns[player]['Board'])
        else:
            possible_actions.extend(self.pawns[player]['Board'])

        return possible_actions, dice_roll
    
    def get_state(self):
        # Convert the current game state into a format that can be used by the Q-learning agent
        state = (tuple(self.board), 
                tuple(tuple(self.pawns[player]['Home']) for player in self.players),
                tuple(tuple(self.pawns[player]['Board']) for player in self.players),
                tuple(tuple(self.pawns[player]['Finished']) for player in self.players))
        return state

    def calculate_capture_risk(self, position, player):
        # Calculate the risk of being captured at a given position
        risk = 0
        for steps_back in range(1, 7):  # Look at the six spaces before the position
            check_position = (position - steps_back) % 28
            if self.board[check_position] and self.board[check_position][0] != player[0]:
                risk += 1  # Increase risk for each opponent's pawn in these spaces
        return risk

    def calculate_reward(self, player, pawn_id, dice_roll):
        # Define weights for different components of the reward
        weights = {
            "move_out_home": -2.320893372179995,
            "move_on_board": -73.767701505335,
            "complete_lap": -18923.15052153681,
            "capture_opponent": -5233.288979969901,
            "risk_change": -55.45727463867416,
            "no_move_penalty": -17.192173275622864
        }

        # Initialize reward
        reward = 0

        if pawn_id in self.pawns[player]['Home'] and dice_roll == 6:
            # Reward for moving a pawn out of home
            reward += weights["move_out_home"]
        elif pawn_id in self.pawns[player]['Board']:
            current_position = self.board.index(pawn_id)
            new_position = (current_position + dice_roll) % 28

            # Reward for moving a pawn on the board
            reward += weights["move_on_board"]

            # Additional reward for completing a lap
            if self.board[self.start_positions[player]] == pawn_id:
                reward += weights["complete_lap"]

            # Check for collisions
            for other_player in self.players:
                if other_player != player:
                    if pawn_id in self.pawns[other_player]['Board']:
                        # Reward for sending an opponent's pawn home
                        reward += weights["capture_opponent"]

            # Calculate risk of capture before and after the move
            risk_before = self.calculate_capture_risk(current_position, player)
            risk_after = self.calculate_capture_risk(new_position, player)

            # Adjust reward based on change in risk
            risk_change = risk_before - risk_after
            reward += risk_change * weights["risk_change"]

        # Penalty for not moving (if no valid moves were possible)
        if len(self.get_possible_actions(player)[0]) == 0:
            reward += weights["no_move_penalty"]

        return reward


    def perform_action(self, player, pawn_id, dice_roll):
        # Perform the action and return the reward and new state
        initial_state = self.get_state()
        self.move_pawn(player, pawn_id, dice_roll)
        new_state = self.get_state()
        reward = self.calculate_reward(player, pawn_id, dice_roll)  # Implement reward calculation
        return reward, new_state



num_games = 10
overall_statistics = {}

for _ in range(num_games):
    game = TroubleGameBasic()
    game.game_statistics = overall_statistics
    winner, turn_count = game.play_game()

print("Overall Statistics:")
for player, stats in overall_statistics.items():
    avg_turns = stats['total_turns'] / stats['wins']
    print(f"{player}: Wins - {stats['wins']}, Average Turns to Win - {avg_turns:.2f}")

