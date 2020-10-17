from random import randint
from flask import Flask, request, render_template, url_for, flash, redirect
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
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)

    def __repr__(self):
        return f"Player('{self.username}')"

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

@app.route('/create_game', methods=['POST'])
def create_game():
    data = request.json
    game = Game(password=randint(100000, 999999))
    db.session.add(game)
    db.session.commit()
    markers = [Location(latitude=float(marker['lat']), longitude=float(marker['long']), game_id=game.id) for marker in data['tasks']]
    for marker in markers:
        db.session.add(marker)
        db.session.commit()
    return str(game.password)


@app.route('/join_game', methods=['POST'])
def join_game():
    data = request.json
    password = data['password']
    if Game.query.filter(password=password):
        game = Game.query.filter(password=password).first()
        player = Player(game_id=game.id)
        db.session.add(player)
        db.session.commit()
        return 'join_game.html'
    return 'You entered the wrong passcode. Try again!'