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


if __name__ == '__main__':
    app.run()
