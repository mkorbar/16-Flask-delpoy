import datetime
import os
import random
import hashlib
import uuid

import requests as requests
from flask import Flask, render_template, request, make_response, redirect
from flask_sqlalchemy import SQLAlchemy

try:
    import secrets
except ImportError:
    # predvidevamo, da nismo v lokalnem okolju
    pass

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite')

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    name = db.Column(db.String, unique=False)
    password = db.Column(db.String, unique=False)
    secret_num = db.Column(db.Integer, unique=False)
    session_token = db.Column(db.String, unique=True)


db.create_all()


@app.route("/")
def index():
    city = 'Postojna'
    api_key = os.getenv('OWM_API_KEY')

    data = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric')
    weather_data = data.json()

    return render_template('index.html', temperature=weather_data['main']['temp'], city=weather_data['name'])


@app.route("/o-meni", methods=['GET', 'POST'])
def oMeni():
    if request.method == 'GET':
        user_name = request.cookies.get('user_name')
        return render_template('o-meni.html', uname=user_name)
    elif request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        print(name)
        print(email)
        print(message)

        response = make_response(render_template('template_message.html', name=name, email=email, message=message))
        response.set_cookie("user_name", name)

        return response


@app.route("/portfolio")
def portfolio():
    return render_template('portfolio.html')


@app.route('/user/')
@app.route('/user/<user_id>')
def user(user_id=None):
    if not user_id:
        user = User.query.filter_by(session_token=request.cookies.get('user_token')).first()
    else:
        user = User.query.filter_by(id=user_id).first()
    return render_template('user_profile.html', user_data=user)


@app.route('/user/edit', methods=['GET', 'POST'])
def user_edit():
    user = User.query.filter_by(session_token=request.cookies.get('user_token')).first()
    if request.method == 'GET':
        return render_template('user_edit.html', user_data=user)
    elif request.method == 'POST':
        user.name = request.form.get('name')
        db.session.add(user)
        db.session.commit()
        return render_template('user_profile.html', user_data=user)


@app.route('/user/delete', methods=['GET', 'POST'])
def user_delete():
    if request.method == 'GET':
        return render_template('user_delete.html')
    else:
        user = User.query.filter_by(session_token=request.cookies.get('user_token')).first()
        db.session.delete(user)
        db.session.commit()
        return redirect('/')


@app.route('/user/list')
def user_list():
    all_users = User.query.all()
    return render_template('user_list.html', users=all_users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        # ??e uporabnik ne obstaja, ustvarimo novega in ga shranimo v bazo
        if not user:
            # v bazi shranjujemo hashed-gesla, ne clear-text
            hashed_pass = hashlib.sha256(password.encode()).hexdigest()
            user = User(email=email, name=name, password=hashed_pass)
            create_new_secret_number_for_user(user)
            message = f'Created a new user {user.name}'
        else:
            # ali se geslo iz baze ujema z geslom iz prijavnega obrazca
            if user.password != hashlib.sha256(password.encode()).hexdigest():
                return render_template('index.html', message='Error logging you in, wrong password')
            # ali se uporabnisko ime iz baze ujema z uporabniskim imenom iz prijavnega obrazca
            if user.name != name:
                return render_template('index.html', message='Error logging you in, wrong user name')
            message = f'Logged in as {user.name}'
        # create a new session id and save it to the DB
        user.session_token = str(uuid.uuid4())
        db.session.add(user)
        db.session.commit()

        response = make_response(render_template('index.html', message=message))
        response.set_cookie('user_token', user.session_token,
                            expires=(datetime.datetime.now() + datetime.timedelta(weeks=1)))
        return response


def create_new_secret_number_for_user(user):
    # save new secret number to db
    user.secret_num = random.randint(1, 30)
    db.session.add(user)
    db.session.commit()


@app.route('/game', methods=['GET', 'POST'])
def guessing_game():
    user_token = request.cookies.get('user_token')
    print(user_token)
    if not user_token:
        return redirect('/login')
    else:
        user = User.query.filter_by(session_token=user_token).first()

    if request.method == 'GET':
        secret_number = user.secret_num
        response = make_response(render_template('game.html', user=user))
        if not secret_number:
            create_new_secret_number_for_user(user)
        return response
    elif request.method == 'POST':

        guess = int(request.form.get("numberGuess"))
        secret_number = user.secret_num

        if guess == secret_number:
            message = "Correct! The secret number is {0}".format(str(secret_number))
            response = make_response(render_template("game.html", message=message, err=False, user=user))

            create_new_secret_number_for_user(user)
            return response
        elif guess > secret_number:
            message = "Your guess is not correct... try something smaller."
            return render_template("game.html", message=message, err=True, user=user)
        elif guess < secret_number:
            message = "Your guess is not correct... try something bigger."
            return render_template("game.html", message=message, err=True, user=user)


if __name__ == '__main__':
    app.run()
