from tempfile import mkdtemp
from flask import Flask, redirect, render_template, session, url_for, make_response, request
from flask_session import Session
from json import load, dumps
from bigboard import BigBoard


app = Flask(__name__)
app.config['SESSION_FILE_DIR'] = mkdtemp()
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


@app.route('/')
def index():
    return redirect(url_for('game'))


@app.route('/game/')
def game():
    if 'board' not in session:
        session['board'] = BigBoard()
    if session['board'].is_over():
        return render_template('game-over.html', board=session['board'].get_board(), winner=session['board'].check_winner())
    else:
        return render_template('game.html', board=session['board'].get_board(), turn=session['board'].get_turn(),
                                            valid=session['board'].get_valid_moves(), choice=session['board'].is_choosing())


@app.route('/new-game/')
def restart_game():
    session['board'] = BigBoard()
    return redirect(url_for('game'))


@app.route('/save-game/')
def save_game():
    if 'board' in session:
        moves = session['board'].get_move_history()
        if moves:
            export = {'start': moves[0][0],
                      'moves': [(b_r, b_c, s_r, s_c) for (_, b_r, b_c, s_r, s_c) in moves]}
            
            response = make_response(dumps(export))
            response.headers.set('Content-Type', 'text/json')
            response.headers.set('Content-Disposition', 'attachment', filename='TicTacCeption-game.json')

            return response

    return redirect(url_for('game'))


@app.route('/load-game/', methods=['POST', 'GET'])
def load_game():
    if request.method == "GET":
        return render_template('load-game.html')

    elif request.method == "POST":
        try:
            if str(request.referrer).replace(request.host_url, '').startswith('load-game'):
                data = load(request.files['game_json'])
                new_game = BigBoard()
                new_game._turn = data['start']
                for move in data['moves']:
                    big_row, big_col, sm_row, sm_col = move
                    new_game.make_move(big_row, big_col, sm_row, sm_col)
                session['board'] = new_game
        except:
            print('Could not load the game.')

    return redirect(url_for('game'))


@app.route('/play/<int:board_row>/<int:board_col>/<int:row>/<int:col>')
def play(board_row, board_col, row, col):
    if 'board' in session:
        valid_moves = session['board'].get_valid_moves()
        if session['board'].is_choosing():
            row, col = valid_moves[board_row, board_col][0]
        if ((board_row, board_col) in valid_moves) and ((row, col) in valid_moves[board_row, board_col]):
            session['board'].make_move(board_row, board_col, row, col)
            session['turn'] = 'O' if session['board'].get_turn() == 'X' else 'X'
    return redirect(url_for('game'))


@app.route('/play-by-play/')
def move_history():
    return render_template('play-by-play.html', moves=session['board'].get_move_history() if 'board' in session else [])


@app.route('/rules/')
def game_rules():
    return render_template('rules.html')


@app.errorhandler(404)
def not_found(exc):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
