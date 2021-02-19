"""smallboard.py

Author: Caio Batista de Melo
Date Created: 2020-11-06
Last Modified: 2020-11-07
Description: Implements a class to keep track of a basic tic-tac-toe game.
"""

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
        if self._winner is not None:
            return self._winner

        # Finds all plays for each row.
        rows = (set(row) for row in self._board)
        # Finds all plays for each column.
        columns = (
            {self._board[j][i] for j in range(len(self._board))}
            for i in range(len(self._board))
        )
        # Finds all plays in the main and reverse diagonals.
        diagonals = (
            {self._board[i][i] for i in range(len(self._board))},  # main diagonal
            {self._board[i][-1 - i] for i in range(len(self._board))},
        )  # reverse diagonal

        for m in chain(rows, columns, diagonals):
            # Check if the same player has taken all positions in this row/col/diag.
            if None not in m and len(m) == 1:
                self._winner = m.pop()
                return self._winner

        return None

    def is_over(self):
        # Check if the game is over (no more open positions or there's a winner).
        return (
            all((None not in row for row in self._board))
            or self.check_winner() is not None
        )

    def get_empty(self):
        # Return a list with the empty positions in the board.
        return [
            (i, j)
            for i in range(len(self._board))
            for j in range(len(self._board))
            if self._board[i][j] is None
        ]

    def get_board(self):
        return self._board
