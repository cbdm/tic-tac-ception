'''smallboard.py

Author: Caio Batista de Melo
Date Created: 2020-11-06
Last Modified: 2020-11-07
Description: Implements a class to keep track of a basic tic-tac-toe game.
'''

from itertools import chain

class SmallBoard(object):
    def __init__(self):
        self._board = [[None for _ in range(3)] for _ in range(3)]
        self._winner = None    


    def make_move(self, x, y, player):
        assert x < len(self._board) and y < len(self._board)
        assert player is not None
        assert self._winner is None

        if self._board[x][y] is None:
            self._board[x][y] = player
            return True
        else:
            return False


    def check_winner(self):
        # Check if we already know the winner.
        if self._winner is not None: return self._winner
        
        # Finds all plays for each row.
        rows = (set(row) for row in self._board) 
        # Finds all plays for each column.
        columns = ({self._board[j][i] for j in range(len(self._board))} for i in range(len(self._board)))
        # Finds all plays in the main and reverse diagonals.
        diagonals = ({self._board[i][i] for i in range(len(self._board))}, # main diagonal
                     {self._board[i][-1-i] for i in range(len(self._board))}) # reverse diagonal

        for m in chain(rows, columns, diagonals):
            # Check if the same player has taken all positions in this row/col/diag.
            if None not in m and len(m) == 1:
                self._winner = m.pop()
                return self._winner

        return None


    def is_over(self):
        # Check if the game is over (no more open positions or there's a winner).
        return all((None not in row for row in self._board)) or self.check_winner() is not None


    def get_empty(self):
        # Return a list with the empty positions in the board.
        return [(i, j) for i in range(len(self._board))
                       for j in range(len(self._board))
                       if self._board[i][j] is None]


    def get_board(self):
        return self._board


    def to_string(self):
        row_format = '| {:^5} | {:^5} | {:^5} |'
        rows = [row_format.format(*(str(x) for x in row)) for row in self._board]
        div = '\n' + max((len(r) for r in rows)) * '-' + '\n'
        return div.join([''] + rows + [''])


    def print_board(self):
        print(self.to_string())


def play_test_game(players=('X', 'O'), turn=0):
    # Create the board and set game-control variables.
    Game = SmallBoard()
    current_player = players[turn]
    turn = (turn + 1) % len(players)

    while not Game.is_over():
        # Show updated board.
        Game.print_board()

        # Get next move from current player.
        x = y = 3
        while x not in range(0, 3) or y not in range(0, 3):
            try:
                x, y = input("Please enter {}'s move in 'x,y' format: ".format(current_player)).split(',')
                x, y = int(x), int(y)
            except ValueError:
                print("Please use 'x,y' format.")
                print("\t-> for example, to play on first row, second column, enter 0,1")

        # Only update the turn if the move was valid.
        if Game.make_move(x, y, current_player):
            current_player = players[turn]
            turn = (turn + 1) % len(players)
        
        else:
            print('\tInvalid move, position is already occupied!')
            print()

    # Show the final board and result.
    Game.print_board()
    winner = Game.check_winner()
    if winner is not None:
        print('\n\tCongrats, {}, you won!!!\n'.format(winner))
    else:
        print("\n\tGame over, it's a tie.\n")


if __name__ == '__main__':
    play_test_game()
