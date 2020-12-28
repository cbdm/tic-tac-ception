'''game.py

Author: Caio Batista de Melo
Date Created: 2020-11-06
Date Modified: 2020-12-28
Description: Sets up the flask server that allows playing the game.
'''

from flask import Flask, redirect, render_template, session, url_for, make_response, request, flash
from json import load, dumps
from bigboard import BigBoard
from ai_options import choose_move


app = Flask(__name__)
app.secret_key = b'\x81^\xaaq\\\x83\x0f4\xf2\x9d\xd7\x08\x12\x0bA\x1a\tVD\x96>\xf3\x180'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/game')
def game():
    if 'board' not in session:
        session['board'] = BigBoard().to_json()
    if 'ai' not in session:
        session['ai'] = False

    board = BigBoard.from_json(session['board'])

    if board.is_over():
        return render_template('game-over.html', board=board.get_board(), winner=board.check_winner())
    elif session['ai'] and board.get_turn() == 'O':
        return make_ai_move()
    else:
        return render_template('game.html', board=board.get_board(), turn=board.get_turn(),
                                            valid=board.get_valid_moves(), choice=board.is_choosing())


@app.route('/start-2P-game')
def start_2P_game():
    session['ai'] = False
    return clear_board()


@app.route('/start-ai-game')
def start_ai_game():
    session['ai'] = True
    session['ai_mode'] = 'random'
    return clear_board()


@app.route('/save-game')
def save_game():
    if 'board' in session:

        moves = BigBoard.from_json(session['board']).get_move_history()
        if moves:
            export = {'ai': session.get('ai', False),
                      'ai_mode': session.get('ai_mode', None),
                      'start': moves[0][0],
                      'moves': [(b_r, b_c, s_r, s_c) for (unused_turn, b_r, b_c, s_r, s_c, unused_choice) in moves]}
            
            response = make_response(dumps(export))
            response.headers.set('Content-Type', 'text/json')
            response.headers.set('Content-Disposition', 'attachment', filename='TicTacCeption-game.json')

            return response

    return redirect(url_for('game'))


@app.route('/load-game', methods=['POST', 'GET'])
def load_game():
    if request.method == "GET":
        return render_template('load-game.html')

    elif request.method == "POST":
        try:
            if str(request.referrer).replace(request.host_url, '').startswith('load-game'):
                data = load(request.files['game_json'])
                session['ai'] = data.get('ai', False)
                session['ai_mode'] = data.get('ai_mode', None)
                if session['ai'] and session['ai_mode'] is None:
                    session['ai_mode'] = 'random'
                new_game = BigBoard()
                new_game._turn = data['start']
                for move in data['moves']:
                    big_row, big_col, sm_row, sm_col = move
                    new_game.make_move(big_row, big_col, sm_row, sm_col)
                session['board'] = new_game.to_json()
        except:
            message = 'Could not load the game.'
            flash(message, 'danger')

    return redirect(url_for('game'))


@app.route('/clear-board')
def clear_board():
    session['board'] = BigBoard().to_json()
    return redirect(url_for('game'))


@app.route('/play/<int:board_row>/<int:board_col>/<int:row>/<int:col>')
def play(board_row, board_col, row, col):
    if 'board' in session:
        board = BigBoard.from_json(session['board'])
        small = str(3*board_row + board_col)
        valid_moves = board.get_valid_moves()
        
        if board.is_choosing():
            row, col = valid_moves[small][0]
        if (small in valid_moves) and ((row, col) in valid_moves[small]):
            board.make_move(board_row, board_col, row, col)
            turn = 'O' if board.get_turn() == 'X' else 'X'
        
        session['board'] = board.to_json()
    
    return redirect(url_for('game'))


@app.route('/make-ai-move')
def make_ai_move():
    if 'board' in session:
        board = BigBoard.from_json(session['board'])
        b_row, b_col, s_row, s_col = choose_move(board, session.get('ai_mode', None))
        return play(b_row, b_col, s_row, s_col)

    return redirect(url_for('game'))


@app.route('/play-by-play')
def move_history():
    if 'board' in session:
        moves = BigBoard.from_json(session['board']).get_move_history()
    else:
        moves = []
    return render_template('play-by-play.html', moves=moves)


@app.route('/rules')
def game_rules():
    return render_template('rules.html')


@app.errorhandler(404)
def not_found(exc):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
