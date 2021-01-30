'''game.py

Author: Caio Batista de Melo
Date Created: 2020-11-06
Date Modified: 2021-01-30
Description: Sets up the flask server that allows playing the game.
'''

from flask import Flask, redirect, render_template, session, url_for, make_response, request, flash, abort
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException
from json import load, dumps
from bigboard import BigBoard
from ai_options import choose_move
from os import getenv
from os.path import exists
from datetime import datetime

app = Flask(__name__)
app.secret_key = getenv('SECRET_KEY', b'\x81^\xaaq\\\x83\x0f4\xf2\x9d\xd7\x08\x12\x0bA\x1a\tVD\x96>\xf3\x180')
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL', 'postgresql:///games_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PREFERRED_URL_SCHEME'] = 'https'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class OnlineGame(db.Model):
    __tablename__ = 'saved_games'

    id = db.Column(db.Integer, primary_key=True)  # Game ID
    timestamp = db.Column(db.String())            # Timestamp of game creation (datetime.utcnow().isoformat())
    xPASS = db.Column(db.String())                # Hashed password for player X
    oPASS = db.Column(db.String())                # Hashed password for player O
    board = db.Column(db.String())                # Current game board

    def __init__(self, timestamp, xPASS, oPASS, board):
        self.timestamp = timestamp
        self.xPASS = xPASS
        self.oPASS = oPASS
        self.board = board


    def __repr__(self):
        return '<id {}>'.format(self.id)


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


@app.route('/online/home')
def online_home():
    return render_template('online-home.html', active_online_id=session.get('active_online_id', None), new_game_id=session.get('newly_created_id', None))


@app.route('/online/create', methods=['POST'])
def online_create():
    base_url_len = len(request.url) - len('/online/create')
    if request.referrer[:base_url_len] == request.url[:base_url_len] and request.referrer[base_url_len:] == '/online/home':

        xPASS = bcrypt.generate_password_hash(request.form.get('xPASS')).decode('utf8') # need to decode because postgres encodes it again when inserting
        oPASS = bcrypt.generate_password_hash(request.form.get('oPASS')).decode('utf8')
        assert xPASS != oPASS, 'The passwords for the players cannot be the same!'        
        
        game_board = BigBoard().to_json()

        new_game = OnlineGame(
            timestamp=datetime.utcnow().isoformat(),
            xPASS=xPASS,
            oPASS=oPASS,
            board=game_board
        )

        db.session.add(new_game)
        db.session.commit()

        session['newly_created_id'] = new_game.id

        return redirect(url_for('online_home'))
    
    return '{}, {}, {}'.format(str(request.referrer), str(request.host_url), str(request.url))
    abort(401)


@app.route('/online/join', methods=['POST'])
def online_join():
    if str(request.referrer).replace(request.host_url, '').startswith('online/home'):
        session['online_player'] = request.form.get('player')
        session['online_pass'] = request.form.get('password')
        session['active_online_id'] = request.form.get('game_id')
        if session.get('newly_created_id', None) == int(session['active_online_id']): del session['newly_created_id']
        return redirect(url_for('online_game'))
    
    abort(401)


@app.route('/online/game')
def online_game():
    if 'active_online_id' not in session:
        return redirect(url_for('online_home'))
    
    game = OnlineGame.query.filter_by(id=session["active_online_id"]).first()
    assert game, 'Unable to get game #{}'.format(session['active_online_id'])

    if session['online_player'] == 'X':
        assert bcrypt.check_password_hash(game.xPASS, session['online_pass']), 'Wrong password for player X in game #{}!'.format(session['active_online_id'])
    else:
        assert bcrypt.check_password_hash(game.oPASS, session['online_pass']), 'Wrong password for player O in game #{}!'.format(session['active_online_id'])
    
    board = BigBoard.from_json(game.board)

    if board.is_over():
        return render_template('game-over.html', board=board.get_board(), winner=board.check_winner())
    elif board.get_turn() != session['online_player']:
        return render_template('online-game.html', board=board.get_board(), turn=board.get_turn(),
                                            valid=[], choice=board.is_choosing(), wait=True, game_id=game.id)
    else:
        return render_template('online-game.html', board=board.get_board(), turn=board.get_turn(),
                                            valid=board.get_valid_moves(), choice=board.is_choosing(), wait=False, game_id=game.id)


@app.route('/online/play/<int:board_row>/<int:board_col>/<int:row>/<int:col>')
def online_play(board_row, board_col, row, col):    
    game = OnlineGame.query.filter_by(id=session["active_online_id"]).first()
    assert game, 'Unable to get game #{}'.format(session['active_online_id'])

    if session['online_player'] == 'X':
        assert bcrypt.check_password_hash(game.xPASS, session['online_pass']), 'Wrong password for player X in game #{}!'.format(session['active_online_id'])
    else:
        assert bcrypt.check_password_hash(game.oPASS, session['online_pass']), 'Wrong password for player O in game #{}!'.format(session['active_online_id'])

    board = BigBoard.from_json(game.board)

    assert session['online_player'] == board.get_turn(), 'Not your turn to move...'
    
    small = str(3*board_row + board_col)
    valid_moves = board.get_valid_moves()
    
    if board.is_choosing():
        row, col = valid_moves[small][0]
    
    if (small in valid_moves) and ((row, col) in valid_moves[small]):
        board.make_move(board_row, board_col, row, col)
    
    game.board = board.to_json()
    db.session.commit()

    return redirect(url_for('online_game'))


@app.route('/online/play-by-play')
def online_move_history():
    game = OnlineGame.query.filter_by(id=session["active_online_id"]).first()
    assert game, 'Unable to get game #{}'.format(session['active_online_id'])
    moves = BigBoard.from_json(game.board).get_move_history()
    return render_template('online-play-by-play.html', moves=moves)


@app.route('/online/save-game')
def online_save_game():
    if "active_online_id" in session:
        game = OnlineGame.query.filter_by(id=session["active_online_id"]).first()
        assert game, 'Unable to get game #{}'.format(session['active_online_id'])
        
        moves = BigBoard.from_json(game.board).get_move_history()
        
        if moves:
            export = {'ai': session.get('ai', False),
                      'ai_mode': session.get('ai_mode', None),
                      'start': moves[0][0],
                      'moves': [(b_r, b_c, s_r, s_c) for (unused_turn, b_r, b_c, s_r, s_c, unused_choice) in moves]}
            
            response = make_response(dumps(export))
            response.headers.set('Content-Type', 'text/json')
            response.headers.set('Content-Disposition', 'attachment', filename='TicTacCeption-game.json')

            return response

    return redirect(url_for('online_game'))


@app.errorhandler(Exception)
def not_found(exc):
    code = exc.code if isinstance(exc, HTTPException) else 500
    return render_template('error.html', code=code, error=str(exc)), code


if __name__ == '__main__':
    app.run(debug=True)
