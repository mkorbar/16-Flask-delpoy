from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/o-meni")
def oMeni():
    return render_template('o-meni.html')


@app.route("/portfolio")
def portfolio():
    return render_template('portfolio.html')


if __name__ == '__main__':
    app.run()
