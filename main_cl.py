'''main_cl.py

Author: Caio Batista de Melo
Date Created: 2021-01-28
Date Modified: 2021-01-28
Description: Runs the game in the command line.
'''

from bigboard import BigBoard

def show_board(board, valid):
    big_row = []
    for i in range(3):
        for ii in range(3):
            big_row.append([])
            for j in range(3):
                small_row = []
                big_board = str(3*i + j)

                for jj in range(3):
                    value = board[i][j].get_board()[ii][jj]
                    if value is None:
                        value = ' '
                    
                    if (ii, jj) in valid.get(big_board, []):
                        value = '*'
                    
                    small_row.append(value)
                big_row[-1].append(' | '.join(small_row))

    for i in range(9):
        print('  ||  '.join(big_row[i]))

        if i % 3 == 2:
            print()

            if i < 8:
                print()
                print('-' * 40)
                print('-' * 40)
                print()
                print()
        
        else:
            print('-' * 40)


def choose_move(player, valid, board_choice):
    print('Valid moves are shown as stars in the board above.')
    print('Choose in the form of "x,y,i,j", where (x, y) indicates the small board you want to play, and (i, j) indicates the position inside that small board.')
    print()

    if not board_choice:
        print('Player {}, make a move!'.format(player))
    
    else:
        print('Player {}, please choose a board for your opponent to play!'.format(player))

    while True:
        try:
            x, y, i, j = (int(a) for a in input('Please choose a valid move [x,y,i,j]: ').split(','))
            if not (i, j) in valid.get(str(3 * x + y), []):
                raise ValueError
            break
        except ValueError:
            print(valid)
            print('Invalid choice!')

    return x, y, i, j


def game_loop():
    board = BigBoard()
    
    while not board.is_over():
        show_board(board.get_board(), board.get_valid_moves())
        big_x, big_y, small_x, small_y = choose_move(board.get_turn(), board.get_valid_moves(), board.is_choosing())
        board.make_move(big_x, big_y, small_x, small_y)

    print()

    winner = board.check_winner()
    if winner is not None:
        print('Congrats {}, you won!'.format(winner))
    
    else:
        print('The game ended in tie...')


def menu():
    keep_playing = True
    game_count = 0

    while keep_playing:
        keep_playing = input('Do you want to play a new game? [Y/n] ').lower() == 'y'
        
        if keep_playing:
            game_count += 1
            game_loop()

    print()
    
    if game_count:
        print('Thanks for playing {} game{}!'.format(game_count, 's' if game_count > 1 else ''))

    else:
        print('Maybe next time :)')


if __name__ == '__main__':
    menu()
