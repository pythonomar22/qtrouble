import random
random.seed("cs221")
from colorDisplay import print_game_board, colors, colorPrint


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
                    self.pawns[player]['Home'].remove(pawn_id)
                    self.pawns[player]['Board'].append(pawn_id)
                    self.board[new_position] = pawn_id
        else:
            if pawn_id in self.pawns[player]['Board'] and pawn_id in self.board:
                current_position = self.board.index(pawn_id)
                new_position = (current_position + steps) % 28
                if new_position != current_position and self.is_valid_move(player, pawn_id, new_position):
                    self.board[current_position] = None
                    self.board[new_position] = pawn_id
                    self.handle_collision(player, new_position)

        self.display_board()

    def handle_collision(self, player, position):
        for other_player, data in self.pawns.items():
            if other_player != player:
                collided_pawn_id = None
                for pawn_id in data['Board']:
                    if int(pawn_id[1:]) == position:  # Check if the pawn is at the collided position
                        collided_pawn_id = pawn_id
                        break
                
                if collided_pawn_id:
                    data['Board'].remove(collided_pawn_id)  # Remove the collided pawn from the board
                    data['Home'].append(collided_pawn_id)  # Send the collided pawn back to home
                    self.board[position] = None  # Clear the position on the board

    def display_board(self):
        board_representation = ['--' if not pawn else pawn for pawn in self.board]
        print_game_board(board_representation)
        #print(" ".join(board_representation))

        #for player, data in self.pawns.items():
        #   print(f"{player}: Home - {data['Home']}, Board - {data['Board']}, Finished - {data['Finished']}")

    def play_game(self):
        while True:
            for player in self.players:
                dice_roll = random.randint(1, 6)
                print(f"{player}'s turn. Dice Roll: {dice_roll}")
                self.take_turn(player, dice_roll)

                if self.check_winner():
                    print(f"{self.check_winner()} wins the game!")
                    return

    def take_turn(self, player, dice_roll):
        if len(self.pawns[player]['Home']) > 0 and dice_roll == 6:
            pawn_id = self.pawns[player]['Home'][0]  # Pawn ready to move out
        elif len(self.pawns[player]['Board']) > 0:
            pawn_id = self.pawns[player]['Board'][0]  # First pawn on the board
        else:
            return  # No move possible

        self.move_pawn(player, pawn_id, dice_roll)  
        print(f"{player} moved {pawn_id} this many spaces: {dice_roll}")

    def check_winner(self):
        """
        Check if any player has won the game.
        """
        for player, data in self.pawns.items():
            if len(data['Finished']) == 4:  # All pawns have finished
                return player
        return None

# Testing the game with collision
game_basic = TroubleGameBasic()
game_basic.play_game()
