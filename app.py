from flask import Flask, render_template, redirect, url_for, session

from db_orm import User, Advert, Order, Purchase, Favourite, Cart

app = Flask(__name__)


@app.route('/')
def home():
    return redirect('/adverts')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/adverts')
def main():
    pass


@app.route('/register')
def register():
    pass


@app.route('/cart')
def cart():
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
