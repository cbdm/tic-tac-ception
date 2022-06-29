"""game.py

Author: Caio Batista de Melo
Date Created: 2020-11-06
Date Modified: 2021-01-30
Description: Sets up the flask server that allows playing the game.
"""

from datetime import datetime
from json import dumps, load
from os import getenv

from flask import (
    Flask,
    abort,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.exceptions import HTTPException

from ai_options import choose_move
from bigboard import BigBoard
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from pymysql import install_as_MySQLdb

install_as_MySQLdb()


class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ["wsgi.url_scheme"] = "https"
        return self.app(environ, start_response)


app = Flask(__name__)
app.secret_key = getenv(
    "SECRET_KEY",
    b"\x81^\xaaq\\\x83\x0f4\xf2\x9d\xd7\x08\x12\x0bA\x1a\tVD\x96>\xf3\x180",
)
db_config = {
    "host": getenv("DB_HOST", "localhost"),
    "port": getenv("DB_PORT", "3306"),
    "user": getenv("DB_USER", "user"),
    "passwd": getenv("DB_PASS", "pass"),
    "database": getenv("DB_NAME", "db"),
}
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "mysql://{user}:{passwd}@{host}:{port}/{database}".format(**db_config)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
if getenv("SECRET_KEY", None) is not None:  # Check if developing locally
    app.wsgi_app = ReverseProxied(app.wsgi_app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class OnlineGame(db.Model):
    __tablename__ = "saved_games"

    id = db.Column(db.Integer, primary_key=True)  # Game ID
    timestamp = db.Column(
        db.Text
    )  # Timestamp of game creation (datetime.utcnow().isoformat())
    xPASS = db.Column(db.Text)  # Hashed password for player X
    oPASS = db.Column(db.Text)  # Hashed password for player O
    board = db.Column(db.Text)  # Current game board

    def __init__(self, timestamp, xPASS, oPASS, board):
        self.timestamp = timestamp
        self.xPASS = xPASS
        self.oPASS = oPASS
        self.board = board

    def __repr__(self):
        return "<id {}>".format(self.id)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/game")
def game():
    if "board" not in session:
        session["board"] = BigBoard().to_json()
    if "ai" not in session:
        session["ai"] = False

    board = BigBoard.from_json(session["board"])

    if board.is_over():
        return render_template(
            "game-over.html", board=board.get_board(), winner=board.check_winner()
        )
    elif session["ai"] and board.get_turn() == "O":
        return make_ai_move()
    else:
        return render_template(
            "game.html",
            board=board.get_board(),
            turn=board.get_turn(),
            valid=board.get_valid_moves(),
            choice=board.is_choosing(),
        )


@app.route("/start-2P-game")
def start_2P_game():
    session["ai"] = False
    return clear_board()


@app.route("/start-ai-game")
def start_ai_game():
    session["ai"] = True
    session["ai_mode"] = "random"
    return clear_board()


@app.route("/save-game")
def save_game():
    if "board" in session:

        moves = BigBoard.from_json(session["board"]).get_move_history()
        if moves:
            export = {
                "ai": session.get("ai", False),
                "ai_mode": session.get("ai_mode", None),
                "start": moves[0][0],
                "moves": [
                    (b_r, b_c, s_r, s_c)
                    for (unused_turn, b_r, b_c, s_r, s_c, unused_choice) in moves
                ],
            }

            response = make_response(dumps(export))
            response.headers.set("Content-Type", "text/json")
            response.headers.set(
                "Content-Disposition", "attachment", filename="TicTacCeption-game.json"
            )

            return response

    return redirect(url_for("game"))


@app.route("/load-game", methods=["POST", "GET"])
def load_game():
    if request.method == "GET":
        return render_template("load-game.html")

    elif request.method == "POST":
        try:
            if (
                str(request.referrer)
                .replace(request.host_url, "")
                .startswith("load-game")
            ):
                data = load(request.files["game_json"])
                session["ai"] = data.get("ai", False)
                session["ai_mode"] = data.get("ai_mode", None)
                if session["ai"] and session["ai_mode"] is None:
                    session["ai_mode"] = "random"
                new_game = BigBoard()
                new_game._turn = data["start"]
                for move in data["moves"]:
                    big_row, big_col, sm_row, sm_col = move
                    new_game.make_move(big_row, big_col, sm_row, sm_col)
                session["board"] = new_game.to_json()
        except Exception:
            message = "Could not load the game."
            flash(message, "danger")

    return redirect(url_for("game"))


@app.route("/clear-board")
def clear_board():
    session["board"] = BigBoard().to_json()
    return redirect(url_for("game"))


@app.route("/play/<int:board_row>/<int:board_col>/<int:row>/<int:col>")
def play(board_row, board_col, row, col):
    if "board" in session:
        board = BigBoard.from_json(session["board"])
        small = str(3 * board_row + board_col)
        valid_moves = board.get_valid_moves()

        if board.is_choosing():
            row, col = valid_moves[small][0]
        if (small in valid_moves) and ((row, col) in valid_moves[small]):
            board.make_move(board_row, board_col, row, col)

        session["board"] = board.to_json()

    return redirect(url_for("game"))


@app.route("/make-ai-move")
def make_ai_move():
    if "board" in session:
        board = BigBoard.from_json(session["board"])
        b_row, b_col, s_row, s_col = choose_move(board, session.get("ai_mode", None))
        return play(b_row, b_col, s_row, s_col)

    return redirect(url_for("game"))


@app.route("/play-by-play")
def move_history():
    if "board" in session:
        moves = BigBoard.from_json(session["board"]).get_move_history()
    else:
        moves = []
    return render_template("play-by-play.html", moves=moves)


@app.route("/rules")
def game_rules():
    return render_template("rules.html")


@app.route("/online/home")
def online_home():
    return render_template(
        "online-home.html",
        active_online_id=session.get("active_online_id", None),
        new_game_id=session.get("newly_created_id", None),
    )


@app.route("/online/create", methods=["POST"])
def online_create():
    if str(request.referrer).replace(request.host_url, "").startswith("online/home"):
        xPASS, oPASS = request.form.get("xPASS"), request.form.get("oPASS")
        assert len(xPASS) in range(
            4, 25
        ), "The password for player X should be between 4 and 24 characters long."
        assert len(oPASS) in range(
            4, 25
        ), "The password for player O should be between 4 and 24 characters long."
        assert xPASS != oPASS, "The passwords for the players cannot be the same!"

        # need to decode because postgres encodes it again when inserting
        xPASS = bcrypt.generate_password_hash(xPASS).decode("utf8")
        oPASS = bcrypt.generate_password_hash(oPASS).decode("utf8")

        game_board = BigBoard().to_json()

        new_game = OnlineGame(
            timestamp=datetime.utcnow().isoformat(),
            xPASS=xPASS,
            oPASS=oPASS,
            board=game_board,
        )

        db.session.add(new_game)
        db.session.commit()

        session["newly_created_id"] = new_game.id

        return redirect(url_for("online_home"))

    abort(401)


@app.route("/online/join", methods=["POST"])
def online_join():
    if str(request.referrer).replace(request.host_url, "").startswith("online/home"):
        game_id = request.form.get("game_id")
        assert (
            len(game_id) <= 6 and game_id.isdigit() and int(game_id) <= 10000
        ), "Invalid Game ID; it should be a number between 1 and 10000"

        player = request.form.get("player")
        assert player in ("X", "O"), "Invalid player selection."

        password = request.form.get("password")
        assert len(password) in range(
            4, 25
        ), "The game password should be between 4 and 24 characters long."

        game = OnlineGame.query.filter_by(id=game_id).first()
        assert game, "Unable to get game #{}".format(game_id)
        assert bcrypt.check_password_hash(
            (game.xPASS if player == "X" else game.oPASS), password
        ), "Wrong password for player {} in game #{}!".format(player, game.id)

        session["online_player"] = player
        session["online_pass"] = game.xPASS if player == "X" else game.oPASS
        session["active_online_id"] = game.id

        if session.get("newly_created_id", None) == session["active_online_id"]:
            del session["newly_created_id"]

        return redirect(url_for("online_game"))

    abort(401)


@app.route("/online/game")
def online_game():
    if "active_online_id" not in session:
        return redirect(url_for("online_home"))

    game = OnlineGame.query.filter_by(id=session["active_online_id"]).first()
    assert game, "Unable to get game #{}".format(session["active_online_id"])
    assert session["online_pass"] == (
        game.xPASS if session["online_player"] == "X" else game.oPASS
    ), "Wrong password for player {} in game #{}!".format(
        session["online_player"], game.id
    )

    board = BigBoard.from_json(game.board)

    if board.is_over():
        return render_template(
            "game-over.html", board=board.get_board(), winner=board.check_winner()
        )
    elif board.get_turn() != session["online_player"]:
        return render_template(
            "online-game.html",
            board=board.get_board(),
            turn=board.get_turn(),
            valid=[],
            choice=board.is_choosing(),
            wait=True,
            game_id=game.id,
        )
    else:
        return render_template(
            "online-game.html",
            board=board.get_board(),
            turn=board.get_turn(),
            valid=board.get_valid_moves(),
            choice=board.is_choosing(),
            wait=False,
            game_id=game.id,
        )


@app.route("/online/play/<int:board_row>/<int:board_col>/<int:row>/<int:col>")
def online_play(board_row, board_col, row, col):
    game = OnlineGame.query.filter_by(id=session["active_online_id"]).first()
    assert game, "Unable to get game #{}".format(session["active_online_id"])
    assert session["online_pass"] == (
        game.xPASS if session["online_player"] == "X" else game.oPASS
    ), "Wrong password for player {} in game #{}!".format(
        session["online_player"], game.id
    )

    board = BigBoard.from_json(game.board)

    assert session["online_player"] == board.get_turn(), "Not your turn to move..."

    small = str(3 * board_row + board_col)
    valid_moves = board.get_valid_moves()

    if board.is_choosing():
        row, col = valid_moves[small][0]

    if (small in valid_moves) and ((row, col) in valid_moves[small]):
        board.make_move(board_row, board_col, row, col)

    game.board = board.to_json()
    db.session.commit()

    return redirect(url_for("online_game"))


@app.route("/online/play-by-play")
def online_move_history():
    moves = []
    if "active_online_id" in session:
        game = OnlineGame.query.filter_by(id=session["active_online_id"]).first()
        assert game, "Unable to get game #{}".format(session["active_online_id"])
        moves = BigBoard.from_json(game.board).get_move_history()
    return render_template("online-play-by-play.html", moves=moves)


@app.route("/online/save-game")
def online_save_game():
    if "active_online_id" in session:
        game = OnlineGame.query.filter_by(id=session["active_online_id"]).first()
        assert game, "Unable to get game #{}".format(session["active_online_id"])

        moves = BigBoard.from_json(game.board).get_move_history()

        if moves:
            export = {
                "ai": session.get("ai", False),
                "ai_mode": session.get("ai_mode", None),
                "start": moves[0][0],
                "moves": [
                    (b_r, b_c, s_r, s_c)
                    for (unused_turn, b_r, b_c, s_r, s_c, unused_choice) in moves
                ],
            }

            response = make_response(dumps(export))
            response.headers.set("Content-Type", "text/json")
            response.headers.set(
                "Content-Disposition", "attachment", filename="TicTacCeption-game.json"
            )

            return response

    return redirect(url_for("online_game"))


@app.route("/code/")
def source_code():
    return redirect("https://github.com/cbdm/tic-tac-ception")


@app.errorhandler(Exception)
def not_found(exc):
    code = exc.code if isinstance(exc, HTTPException) else 500
    return render_template("error.html", code=code, error=str(exc)), code


if __name__ == "__main__":
    app.run(debug=True)
