"""ai_options.py

Author: Caio Batista de Melo
Date Created: 2020-12-28
Date Modified: 2020-12-28
Description: Defines the different types of AI available.
"""

from random import choice

from bigboard import BigBoard


class Random:
    def choose_best_move(board):
        valid_moves = board.get_valid_moves()
        small_board = choice(list(valid_moves))
        row, col = int(small_board) // 3, int(small_board) % 3
        x, y = choice(valid_moves[small_board])
        return row, col, x, y


def choose_move(board, ai):
    assert isinstance(board, BigBoard)
    return Random.choose_best_move(board)
