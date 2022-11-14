from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from db_orm import User, Advert, Order, Purchase, Favorite, Cart

app = Flask(__name__)
app.config['SECRET_KEY'] = 'd7dcef09a8c584b32d85a9b09730edf824347958'
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get_all(id=user_id)


@app.route('/')
def home():
    return redirect('/adverts')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/adverts')
def main():
    adverts = Advert.get_all(user_id='not null')
    if not isinstance(adverts, list):
        adverts = [adverts]
    context = {
        'adverts': adverts,
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


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('pwd')
        password2 = request.form.get('pwd2')

        if not (email or password or password2):
            flash('Please, fill all fields! However, you can leave the name field empty')

        elif password != password2:
            flash('Passwords are not equal!')

        else:
            if User.get_all(email=email):
                flash('Have user with this email')
            else:
                user = User(email, password, name)
                user.save()

                return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pwd')
        user = User.get_all(email=email)
        if email and password:
            if user and User.check_password(password, user.password):
                if request.form.get('remember'):
                    login_user(user, remember=True)
                else:
                    login_user(user)

                next_page = request.args.get('next')
                if not next_page:
                    next_page = url_for('main')

                return redirect(next_page)
            else:
                flash('Login or password is not correct')
        else:
            flash('Please fill login and password fields')
    return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('main'))


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login') + '?next=' + request.url)

    return response


@app.route('/add_advert', methods=['GET', 'POST'])
@login_required
def add_advert():
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')
        cat = request.form.get('cat')
        cost = request.form.get('cost')
        img_url = request.form.get('img_url')
        user_id = current_user.id

        adv = Advert(title, desc, cat, cost, img_url, user_id)

        adv.save()

        return redirect(url_for('main', id=adv.id))

    return render_template('add_advert.html')


@app.route('/advert/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_advert(id):
    advert = Advert.get_all(id=id)
    if current_user.id == advert.user_id:

        context = {
            'advert': advert
        }

        if request.method == 'POST':
            new_data = {
                'title': request.form.get('title'),
                'description': request.form.get('desc'),
                'category': request.form.get('cat'),
                'cost': request.form.get('cost'),
                'image_url': request.form.get('img_url'),
                'user_id': current_user.id
            }

            advert.update(**new_data)

            return redirect(url_for('advert', id=id))
        return render_template('edit_advert.html', **context)
    return redirect(url_for('advert', id=id))


@app.route('/advert/<int:id>/delete')
@login_required
def delete_advert(id):
    adv = Advert.get_all(id=id)
    print(adv)
    if current_user.id == adv.user_id or current_user.admin_status:
        adv.__delete__()
        return redirect(url_for('main'))
    return redirect(url_for('advert', id=id))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/cart')
def cart():
    pass


@app.route('/favorites')
@login_required
def favorites():
    pass


@app.route('/orders')
@login_required
def orders():
    pass


@app.route('/personal_account')
def personal_account():
    pass


if __name__ == '__main__':
    app.run()
