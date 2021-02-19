"""generate_games.py

Author: Caio Batista de Melo
Date Created: 2020-12-28
Date Modified: 2020-12-28
Description: Generates random games that can be used to train AI models.
"""

import argparse
from json import dumps
from math import ceil
from sys import stdout

from ai_options import Random
from bigboard import BigBoard


def generate_n_games(n, verbose, pct):
    games = {}
    parts = ceil(n * 0.01 * pct)

    for i in range(n):
        if verbose and i % parts == 0:
            print(f"Generating game #{i} ({((i+1)/n)*100:.2f}%)")

        new_game = BigBoard()
        while not new_game.is_over():
            row, col, x, y = Random.choose_best_move(new_game)
            new_game.make_move(row, col, x, y)

        games[f"game#{i}"] = {
            "moves": new_game.get_move_history(),
            "winner": new_game.check_winner(),
        }

    if verbose:
        print("Done")

    return games


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This script generates random games.")
    parser.add_argument(
        "-o",
        "--out",
        help="filename to export the games played",
        nargs="?",
        type=argparse.FileType("w"),
        default=stdout,
    )
    parser.add_argument(
        "-n", "--num", help="how many games it should generate", default=10, type=int
    )
    parser.add_argument("-v", "--verbose", default=True, type=bool)
    parser.add_argument(
        "-p",
        "--pct",
        help="percentage of completion to display in verbose output",
        default=5,
        type=float,
    )
    args = parser.parse_args()

    games = generate_n_games(args.num, args.verbose, args.pct)

    args.out.write(dumps(games))
    args.out.close()
