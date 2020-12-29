'''parse_generated_games.py

Author: Caio Batista de Melo
Date Created: 2020-12-28
Date Modified: 2020-12-28
Description: Read generated games and creates a feature set.
'''

import argparse
from json import load
from bigboard import BigBoard

def rate_moves(player_moves, outcome):
    return [outcome * ((0.9) ** i) for i in range(len(player_moves))][::-1]


def convert_board_to_int(small_board):
    num = 0
    for i in range(len(small_board)):
        power = 3 ** i
        num += small_board[-1-i] * power
    return num


def split_game(moves):
    new_game = BigBoard()
    player_0 = []
    player_1 = []
    new_game.turn = p0 = moves[0][0]
    
    for i, m in enumerate(moves):
        all_cells = new_game.get_board()
        small_wins = [all_cells[i][j].check_winner() for j in range(3) for i in range(3)]
        small_wins = [2 if small_wins[3*i+j] == new_game.get_turn() else (1 if small_wins[3*i+j] is None else 0) for j in range(3) for i in range(3)]
        small_wins = convert_board_to_int(small_wins)

        small_boards = []
        for i in range(3):
            for j in range(3):
                cur_board = all_cells[i][j].get_board()
                cur_board = [2 if cur_board[i][j] == new_game.get_turn() else (1 if cur_board[i][j] is None else 0) for j in range(3) for i in range(3)]
                cur_board = convert_board_to_int(cur_board)
                small_boards.append(cur_board)

        move_data = [small_wins, *small_boards, m[1:]]
        if m[0] == p0:
            player_0.append(move_data)
        else:
            player_1.append(move_data)

        new_game.make_move(*m[1:-1])

    return player_0, player_1


def parse_data(games, scoring_function=rate_moves):
    data = []
    scores = []
    for game in games.values():
        player_0, player_1 = split_game(game['moves'])
        result = 1 if game['winner'] == game['moves'][0][0] else 0 if game['winner'] is None else -1
        data.extend(player_0)
        scores.extend(scoring_function(player_0, result))
        data.extend(player_1)
        scores.extend(scoring_function(player_1, -result))
    return data, scores


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This script generates random games.')
    parser.add_argument('-f', '--file', help='filename to read the generated games', required=True, type=argparse.FileType('r'))
    args = parser.parse_args()
    games = load(args.file)
    X, y = parse_data(games)
    print('Sample data point:', X[0])
    print('Sample score:', y[0])
