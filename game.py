from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from forms import CreateGameForm, JoinGameForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)

    def __repr__(self):
        return f"Player('{self.username}')"


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    password = db.Column()
    players = db.relationship('Player', backref='player', lazy=True)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/create_game", methods=['GET', 'POST'])
def register():
    form = CreateGameForm()
    if form.validate_on_submit():
        flash(f'Game created! Join at { password }.', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

'''
@app.route("/join_game", methods=['GET', 'POST'])
def login():
    form = JoinGameForm()
    if form.validate_on_submit():
        if Game.query.filter_by(form.password.data):
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)
'''

if __name__ == '__main__':
    app.run(debug=True)