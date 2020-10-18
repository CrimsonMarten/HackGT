from random import randint
from flask import Flask, request, render_template, url_for, flash, redirect, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import json

app = Flask(__name__)
Api = Api(app)
CORS(app)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)


if __name__ == '__main__':
    app.run(debug=True)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    is_alive = db.Column(db.Boolean, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)

    def __repr__(self):
        return f"Location('Latitude: {self.latitude}, 'Longitude: {self.longitude}')"

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.Integer, nullable=False)
    players = db.relationship('Player', backref='player', lazy=True)
    markers = db.relationship('Location', backref='marker', lazy=True)
    marker_string = db.Column(db.String())
    tasks = db.Column(db.Integer)
    total_tasks = db.Column(db.Integer)

@app.route('/create_game', methods=['POST'])
def create_game():
    data = request.json
    game = Game(password=randint(100000, 999999), marker_string=request.data)
    db.session.add(game)
    db.session.commit()
    markers = [Location(latitude=float(marker['lat']), longitude=float(marker['long']), game_id=game.id) for marker in data['tasks']]
    for marker in markers:
        db.session.add(marker)
        db.session.commit()
    return str(game.password)


@app.route('/join_game', methods=['POST'])
def join_game():
    data = request.data
    data = json.loads(data)
    print(data)
    username, password, lat, lng = data['username'], int(data['password']), float(data['lat']), float(data['long'])
    if Game.query.filter_by(password=password):
        game = Game.query.filter_by(password=password).first()
        player = Player(game_id=game.id, is_alive=True, latitude=lat, longitude=lng, username=username)
        db.session.add(player)
        db.session.commit()
        json_data = json.loads(game.marker_string)
        players = len(list(Player.query.filter_by(game_id=game.id)))
        game.total_tasks = players * len(json_data['tasks'])
        json_data['id'] = player.id
        json_data['num_tasks'] = game.total_tasks
        game.tasks = game.total_tasks
        db.session.commit()
        return json.dumps(json_data)

    return 'You entered the wrong passcode. Try again!'

@app.route('/current_tasks', methods=['POST'])
def current_tasks():
    data = request.data
    password = int(data)
    print(password)
    game = Game.query.filter_by(password=password).first()
    return jsonify({ 'total': game.total_tasks, 'incomplete': game.tasks})

@app.route('/update_tasks', methods=['POST'])
def update_tasks():
    data = request.data
    password = int(data)
    game = Game.query.filter_by(password=password).first()
    game.tasks = game.tasks - 1
    db.session.commit()
    return str(game.tasks)


@app.route('/update_player_location', methods=['POST'])
def update_player_location() :
    data = request.data
    data = json.loads(data)
    print("DATA")
    print(data)
    player_id = int(data['playerID'])
    new_lat = float(data['lat'])
    new_long = float(data['long'])
    player = Player.query.filter_by(id=player_id).first()

    player.latitude = new_lat
    player.longitude = new_long

    db.session.commit()

    return str(player.is_alive)


@app.route('/get_players_in_game', methods=['POST'])
def get_players_in_game() :
    data = request.data
    print("DATA")
    print(data)
    game_id = int(data)
    players = []
    game = Game.query.filter_by(password=game_id).first()
    for player in list(Player.query.filter_by(game_id=game.id)):
        players.append({'uid': player.id, 'lat': player.latitude, 'long': player.longitude, 'alive': player.is_alive, 'username': player.username})

    return jsonify({ 'players': players })

@app.route('/kill', methods=['POST'])
def kill():
    data = request.data
    data = json.loads(data)
    killer_id = int(data['killerID'])
    victim_id = int(data['victimID'])
    victim = Player.query.filter_by(id=victim_id).first()
    victim.is_alive = False
    db.session.commit()
    return ''

