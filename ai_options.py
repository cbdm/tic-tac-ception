'''ai_options.py

Author: Caio Batista de Melo
Date Created: 2020-12-28
Date Modified: 2020-12-28
Description: Defines the different types of AI available.
'''


from random import choice
from bigboard import BigBoard


class Random:
    def choose_best_move(board):
        small = int(choice(list(board.get_valid_moves())))
        row, col = small//3, small%3
        empty_moves = board.get_board()[row][col].get_empty()
        x, y = choice(empty_moves)
        return row, col, x, y


def choose_move(board, ai):
    assert isinstance(board, BigBoard)
    return Random.choose_best_move(board)
