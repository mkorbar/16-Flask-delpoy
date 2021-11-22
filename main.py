import random

from flask import Flask, render_template, request, make_response

app = Flask(__name__)


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


@app.route('/game', methods=['GET', 'POST'])
def guessing_game():
    if request.method == 'GET':
        secret_number = request.cookies.get('secret_number')
        response = make_response(render_template('game.html'))
        if not secret_number:
            secret_number = random.randint(1, 30)
            response.set_cookie('secret_number', str(secret_number))
        return response
    elif request.method == 'POST':

        guess = int(request.form.get("numberGuess"))
        secret_number = int(request.cookies.get("secret_number"))

        if guess == secret_number:
            message = "Correct! The secret number is {0}".format(str(secret_number))
            response = make_response(render_template("game.html", message=message, err=False))
            response.set_cookie("secret_number", str(random.randint(1, 30)))  # set the new secret number
            return response
        elif guess > secret_number:
            message = "Your guess is not correct... try something smaller."
            return render_template("game.html", message=message, err=True)
        elif guess < secret_number:
            message = "Your guess is not correct... try something bigger."
            return render_template("game.html", message=message, err=True)


if __name__ == '__main__':
    app.run()
