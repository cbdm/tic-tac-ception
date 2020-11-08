'''bigboard.py

Author: Caio Batista de Melo
Date Created: 2020-11-06
Date Modified: 2020-11-08
Description: Implements the logic for the Tic-Tac-Ception game and a basic terminal interface.
'''

from smallboard import SmallBoard
from random import randint
from itertools import chain
from jsonpickle import encode, decode

class BigBoard(object):
    def __init__(self):
        self._board = [[SmallBoard() for _ in range(3)] for _ in range(3)]
        self._winner = None
        self._history = []
        self._players = ('X', 'O')
        self._turn = self._players[1] if randint(0, 1) else self._players[0]
        self._possible_moves = {str(3*i + j): self._board[i][j].get_empty()
                                        for i in range(len(self._board))
                                        for j in range(len(self._board))
                                        if not self._board[i][j].is_over()
                                }
        self._choosing_board = False


    def _find_possible_moves(self, last_x, last_y):
        if self._board[last_x][last_y].is_over():
            winner = self._board[last_x][last_y].check_winner()
            self._choosing_board = winner == self._turn
            self._possible_moves = {str(3*i + j): self._board[i][j].get_empty()
                                            for i in range(len(self._board))
                                            for j in range(len(self._board))
                                            if not self._board[i][j].is_over()
                                    }

        else:
            self._choosing_board = False
            self._possible_moves = {str(3*last_x + last_y): self._board[last_x][last_y].get_empty()}

        if not self._choosing_board:
            self._turn = self._players[1] if self._players[0] == self._turn else self._players[0]


    def make_move(self, board_x, board_y, move_x, move_y):
        if self._choosing_board:
            self._find_possible_moves(board_x, board_y)            
            
        elif str(3 * board_x + board_y) in self._possible_moves and (move_x, move_y) in self._possible_moves[str(3*board_x + board_y)]:
            self._board[board_x][board_y].make_move(move_x, move_y, self._turn)
            self._history.append((self._turn, board_x, board_y, move_x, move_y))
            if not self.is_over():
                self._find_possible_moves(move_x, move_y)
            else:
                self._possible_moves = {}


    def is_choosing(self):
        return self._choosing_board


    def is_over(self):
        over = (self._board[i][j].is_over() for j in range(3) for i in range(3))
        return all(over) or self.check_winner() is not None


    def check_winner(self):
        # Check if we already know the winner.
        if self._winner is not None: return self._winner
        
        # Gets the winner from each small board.
        small_wins = [[self._board[i][j].check_winner() for j in range(3)] for i in range(3)]
        
        # Finds all plays in each row.
        rows = (set(row) for row in small_wins) 
        # Finds all plays in each column.
        columns = ({small_wins[j][i] for j in range(3)} for i in range(3))
        # Finds all plays in the main and reverse diagonals.
        diagonals = ({small_wins[i][i] for i in range(3)}, # main diagonal
                     {small_wins[i][-1-i] for i in range(3)}) # reverse diagonal

        for m in chain(rows, columns, diagonals):
            # Check if the same player has taken all positions in this row/col/diag.
            if None not in m and len(m) == 1:
                # Set the winner and returns.
                self._winner = m.pop()
                return self._winner

        # Check if all small boards are over, if they are, the winner is whoever has the most small wins.
        over = (self._board[i][j].is_over() for j in range(3) for i in range(3))
        if all(over):
            count = 0
            for row in small_wins:
                for win in small_wins:
                    if win == self._players[0]:
                        count -= 1
                    elif win == self._players[1]:
                        count += 1
            if count < 0:
                self._winner = self._players[0]
                return self._winner
            elif count > 0:
                self._winner = self._players[1]
                return self._winner

        return None


    def get_move_history(self):
        return self._history


    def get_board(self):
        return self._board


    def get_turn(self):
        return self._turn


    def get_valid_moves(self):
        return self._possible_moves


    def to_json(self):
        return encode(self)


    def from_json(json):
        return decode(json)


    def to_string(self):
        out= ''

        all_rows = []
        for big_board_i in range(len(self._board)):
            for small_board_i in range(len(self._board)):
                current_row = []
                for big_board_j in range(len(self._board)):
                    for small_board_j in range(len(self._board)):
                        current_row.append(self._board[big_board_i][big_board_j]._board[small_board_i][small_board_j])
                all_rows.append(current_row)
        
        big_row_format = (('{:^5} | ' * (len(self._board) - 1) + '{:^5}') + '   ||   ') * (len(self._board) - 1) + ('{:^5} | ' * (len(self._board) - 1) + '{:^5}') + '\n'
        small_div = (((5*'-' + '-+-') * (len(self._board) - 1) + 5*'-')  + '---++---') * (len(self._board) - 1) + ((5*'-' + '-+-') * (len(self._board) - 1) + 5*'-') + '\n'
        big_div = ((((5+3) * len(self._board) * '-') + '||---') * (len(self._board) - 1)) + (((5+3) * len(self._board) - 3) * '-') + '\n'

        for big_board_i in range(len(self._board)):
            for small_board_i in range(len(self._board)):
                out+= big_row_format.format(*[str(x) for x in all_rows[3*big_board_i+small_board_i]])
                if small_board_i != len(self._board) - 1:
                    out+= small_div
            if big_board_i != len(self._board) - 1:
                out+= big_div
                out+= big_div

        return out


    def print_board(self):
        print(self.to_string())


    def print_valid_moves(self):
        print('Valid moves:')
        for b in self._possible_moves:
            print('\tBoard {},{}: {}'.format(x, y, self._possible_moves[b]))


    def print_turn(self):
        print("It's player {}'s turn!".format(self._turn))


def get_move():
    board_x = board_y = move_x = move_y = 3
    while board_x not in range(0, 3) or board_y not in range(0, 3) \
            or move_x not in range(0, 3) or move_y not in range(0, 3):
        try:
            board_x, board_y, move_x, move_y = input("Please choose a valid move (use 'i,j,x,y' format): ").split(',')
            board_x, board_y, move_x, move_y = int(board_x), int(board_y), int(move_x), int(move_y)
        except ValueError:
            print()
            print()
            print('!' * 20)
            print('ERROR!')
            print("Please use 'i,j,x,y' format.")
            # print("Please make sure the move is valid and use 'i,j,x,y' format.")
            print("\t-> for example, to play in the the center board(1,1), on the top-right(0,2) position, enter 1,1,0,2")
            print('!' * 20)
            print()

    return board_x, board_y, move_x, move_y


def play_test_game():
    Game = BigBoard()
    while not Game.is_over():
        Game.print_board()
        Game.print_turn()
        Game.print_valid_moves()
        board_x, board_y, move_x, move_y = get_move()
        Game.make_move(board_x, board_y, move_x, move_y)
        
    winner = Game.check_winner()
    if winner is not None:
        print('\n\tCongrats, {}, you won!!!\n'.format(winner))
    else:
        print("\n\tGame over, it's a tie.\n")


if __name__ == '__main__':
    play_test_game()
