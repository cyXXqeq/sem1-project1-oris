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
    adverts = Advert.get_all()
    if session.get('user_id'):
        user = User.get_all(id=session['user_id'])
    else:
        user = None
    context = {
        'adverts': adverts,
        'user': user
    }
    return render_template('main.html', **context)


@app.route('/advert/<int:id>/')
def advert(id):
    adv = Advert.get_all(id=id)
    owner = User.get_all(id=adv.user_id).name
    if session.get('user_id'):
        user = User.get_all(id=session['user_id'])
    else:
        user = None
    context = {
        'advert': adv,
        'user': user,
        'owner': owner
    }
    return render_template('advert.html', **context)


@app.route('/login')
def login():
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
