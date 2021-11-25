import os
import random
import hashlib
from flask import Flask, render_template, request, make_response, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite')

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    name = db.Column(db.String, unique=False)
    password = db.Column(db.String, unique=False)
    secret_num = db.Column(db.Integer, unique=False)


db.create_all()

@app.route("/")
def index():
    return render_template('index.html')


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        # če uporabnik ne obstaja, ustvarimo novega in ga shranimo v bazo
        if not user:
            # v bazi shranjujemo hashed-gesla, ne clear-text
            hashed_pass = hashlib.sha256(password.encode()).hexdigest()
            user = User(email=email, name=name, password=hashed_pass)
            db.session.add(user)
            db.session.commit()
        else:
            # ali se geslo iz baze ujema z geslom iz prijavnega obrazca
            if user.password != hashlib.sha256(password.encode()).hexdigest():
                return render_template('index.html', message='Error logging you in, wrong password')
            # ali se uporabnisko ime iz baze ujema z uporabniskim imenom iz prijavnega obrazca
            if user.name != name:
                return render_template('index.html', message='Error logging you in, wrong user name')

        response = make_response(render_template('index.html', message='You were successfully logged in'))
        response.set_cookie('user_email', email)
        return response


def create_new_secret_number_for_user(user):
        # save new secret number to db
        user.secret_num = random.randint(1, 30)
        db.session.add(user)
        db.session.commit()


@app.route('/game', methods=['GET', 'POST'])
def guessing_game():

    user_email = request.cookies.get('user_email')
    if not user_email:
        return redirect('/login')
    else:
        user = User.query.filter_by(email=user_email).first()

    if request.method == 'GET':
        secret_number = user.secret_num
        response = make_response(render_template('game.html'))
        if not secret_number:
            create_new_secret_number_for_user(user)
        return response
    elif request.method == 'POST':

        guess = int(request.form.get("numberGuess"))
        secret_number = user.secret_num

        if guess == secret_number:
            message = "Correct! The secret number is {0}".format(str(secret_number))
            response = make_response(render_template("game.html", message=message, err=False))

            create_new_secret_number_for_user(user)
            return response
        elif guess > secret_number:
            message = "Your guess is not correct... try something smaller."
            return render_template("game.html", message=message, err=True)
        elif guess < secret_number:
            message = "Your guess is not correct... try something bigger."
            return render_template("game.html", message=message, err=True)


if __name__ == '__main__':
    app.run()
