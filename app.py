from flask import Flask

app = Flask(__name__)


@app.route('/')
def main():
    pass


@app.route('/register')
def register():
    pass


@app.route('/basket')
def basket():
    pass


@app.route('/favourites')
def favourites():
    pass


@app.route('/orders')
def orders():
    pass


@app.route('/personal_account')
def personal_account():
    pass


if __name__ == '__main__':
    app.run()
