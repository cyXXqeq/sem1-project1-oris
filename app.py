import bcrypt
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from db_orm import User, Advert, Order, Purchase, Favorite, Cart

app = Flask(__name__)
app.config['SECRET_KEY'] = "d7dcef09a8c584b32d85a9b09730edf824347958"
login_manager = LoginManager(app)

categories = [
    'clothing',
    'tools',
    'entertainment',
    'shoes',
    'accessories',
    'jewelry',
    'appliances',
    'food',
    'other'
]


@login_manager.user_loader
def load_user(user_id):
    return User.get_all(id=user_id)


@app.route('/')
def home():
    return redirect('/adverts')


@app.route('/adverts', methods=['GET'])
def main():
    category = request.args.get('category')
    search = request.args.get('search')
    filters = {
        'user_id': 'not null',
        'is_active': True,
        'category': category,
        'search': search
    }

    adverts = Advert.get_all(**filters)
    if not isinstance(adverts, list):
        adverts = [adverts]

    if not search:
        search = ''
    context = {
        'adverts': adverts,
        'search': search,
        'categories': categories
    }
    return render_template('main.html', **context)


@app.route('/advert/<int:page_id>/')
def advert(page_id):
    adv = Advert.get_all(id=page_id)
    if adv.user_id:
        owner = User.get_all(id=adv.user_id).name
    else:
        owner = '<deleted account>'
    context = {
        'advert': adv,
        'owner': owner,
        'categories': categories,
        'in_cart': True if Cart.get_all(user_id=current_user.id, advert_id=page_id) else False,
        'in_favorite': True if Favorite.get_all(user_id=current_user.id, advert_id=page_id) else False
    }
    return render_template('advert.html', **context)


@app.route('/register', methods=['GET', 'POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    image_url = request.form.get('image_url')
    context = {'categories': categories}

    for field, field_name in [(name, 'name'), (email, 'email'), (image_url, 'image_url')]:
        if field:
            context[field_name] = field
        else:
            context[field_name] = ''

    if request.method == 'POST':
        password = request.form.get('pwd')
        password2 = request.form.get('pwd2')

        if email and password and password2:
            if password != password2:
                flash('Passwords are not equal!')
            else:
                if User.get_all(email=email):
                    flash('Have user with this email')
                else:
                    user = User(email, password, name, image_url)
                    user.save()

                    return redirect(url_for('login'))

        else:
            flash('Please, fill all fields! However, you can leave the name field empty')

    return render_template('register.html', **context)


@app.route('/login', methods=['GET', 'POST'])
def login():
    email = request.form.get('email')
    if request.method == 'POST':
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
    if not email:
        email = ''
    return render_template('login.html', categories=categories, email=email)


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
    context = {
        'title': request.form.get('title'),
        'description': request.form.get('desc'),
        'category': request.form.get('cat'),
        'cost': request.form.get('cost'),
        'image_url': request.form.get('img_url'),
        'user_id': current_user.id
    }

    if request.method == 'POST':

        if context['title'] and context['description'] and context['category'] and context['cost']:
            adv = Advert(**context)
            adv.save()

            return redirect(url_for('advert', page_id=adv.id))

        flash('Title, description, category and cost are required fields! Please, enter this fields.')

    for key in context:
        if context[key] is None:
            context[key] = ''
    context['categories'] = categories

    return render_template('add_advert.html', **context)


@app.route('/advert/<int:page_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_advert(page_id):
    adv = Advert.get_all(id=page_id)
    if current_user.id == adv.user_id:

        context = {
            'title': adv.title,
            'description': adv.description,
            'category': adv.category,
            'cost': adv.cost,
            'image_url': adv.image_url,
            'user_id': adv.user_id,
            'id': adv.id,
            'categories': categories
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

            if new_data['title'] and new_data['description'] and new_data['category'] and new_data['cost']:
                adv.update(**new_data)

                return redirect(url_for('advert', page_id=page_id))

            flash('Title, description, category and cost are required fields! Please, enter this fields.')

        for key in context:
            if context[key] is None:
                context[key] = ''

        return render_template('edit_advert.html', **context)
    return redirect(url_for('advert', page_id=page_id))


@app.route('/advert/<int:page_id>/delete')
@login_required
def delete_advert(page_id):
    adv = Advert.get_all(id=page_id)
    if current_user.id == adv.user_id or current_user.admin_status:
        adv.delete()
        return redirect(url_for('main'))
    return redirect(url_for('advert', id=page_id))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', categories=categories)


@app.route('/profile/delete')
@login_required
def delete_profile():
    user = current_user
    user.delete()
    return redirect(url_for('main'))


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    context = {
        'email': current_user.email,
        'name': current_user.name,
        'image_url': current_user.image_url,
        'categories': categories
    }

    if request.method == 'POST':
        new_data = {
            'email': request.form.get('email'),
            'name': request.form.get('name'),
        }
        image_url = request.form.get('image_url')
        password = request.form.get('password')
        password_retype = request.form.get('password2')

        if image_url:
            new_data['image_url'] = image_url

        if new_data['email']:
            if password:
                if password_retype:
                    if password == password_retype:
                        new_data['password'] = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).hex()
                    else:
                        flash("Passwords don't match!")
                        return render_template('edit_profile.html', **context)
                else:
                    flash("Enter password retype!")
                    return render_template('edit_profile.html', **context)

            current_user.update(**new_data)

            return redirect(url_for('profile'))

        flash('Email a required field! Please, enter email.')

    return render_template('edit_profile.html', **context)


@app.route('/cart')
@login_required
def cart():
    in_cart = Cart.get_all(user_id=current_user.id)
    if not isinstance(in_cart, list):
        in_cart = [in_cart]
    advs_in_cart = []
    for adv_in_cart in in_cart:
        advs = Advert.get_all(id=adv_in_cart.advert_id)
        if not isinstance(advs, list):
            advs = [advs]
        advs_in_cart += advs

    summa = sum([adv.cost for adv in advs_in_cart])

    context = {
        'adverts': advs_in_cart,
        'summa': summa,
        'categories': categories
    }

    return render_template('cart.html', **context)


@app.route('/advert/<int:page_id>/add_to_cart')
@login_required
def add_to_cart(page_id):
    if not Cart.get_all(user_id=current_user.id, advert_id=page_id):
        adv_in_cart = Cart(current_user.id, page_id)
        adv_in_cart.save()
    return redirect(url_for('advert', page_id=page_id))


@app.route('/cart/delete/<int:adv_id>/<int:from_advert>')
@login_required
def delete_from_cart(adv_id, from_advert):
    adv_in_cart = Cart.get_all(user_id=current_user.id, advert_id=adv_id)
    adv_in_cart.delete()
    if from_advert:
        return redirect(url_for('advert', page_id=adv_id))
    return redirect(url_for('cart'))


@app.route('/favorites')
@login_required
def favorites():
    search = request.args.get('search')
    if not search:
        search = ''
    in_favorites = Favorite.get_all(user_id=current_user.id)
    if not isinstance(in_favorites, list):
        in_favorites = [in_favorites]
    advs_in_favorites = []
    for adv_in_fav in in_favorites:
        advs = Advert.get_all(id=adv_in_fav.advert_id, search=search)
        if not isinstance(advs, list):
            advs = [advs]
        advs_in_favorites += advs

    context = {
        'adverts': advs_in_favorites,
        'categories': categories
    }

    return render_template('favorites.html', **context)


@app.route('/advert/<int:page_id>/add_to_favorites')
@login_required
def add_to_favorites(page_id):
    if not Favorite.get_all(user_id=current_user.id, advert_id=page_id):
        adv_to_favorites = Favorite(current_user.id, page_id)
        adv_to_favorites.save()
    return redirect(url_for('advert', page_id=page_id))


@app.route('/favorites/delete/<int:adv_id>/<int:from_advert>')
@login_required
def delete_from_favorites(adv_id, from_advert):
    adv_in_fav = Favorite.get_all(user_id=current_user.id, advert_id=adv_id)
    adv_in_fav.delete()
    if from_advert:
        return redirect(url_for('advert', page_id=adv_id))
    return redirect(url_for('favorites'))


@app.route('/make_order')
@login_required
def make_order():
    advs_in_cart = Cart.get_all(user_id=current_user.id)

    if not isinstance(advs_in_cart, list):
        advs_in_cart = [advs_in_cart]

    advs = [Advert.get_all(id=adv_in_cart.advert_id) for adv_in_cart in advs_in_cart]
    summa = sum([adv.cost for adv in advs])
    order = Order(summa, current_user.id)
    order.save()

    for adv in advs:
        purch = Purchase(adv.id, order.id)
        purch.save()
        adv.hidden()

    for adv_in_cart in advs_in_cart:
        adv_in_cart.delete()

    return redirect(url_for('orders_page'))


@app.route('/orders')
@login_required
def orders_page():
    orders = Order.get_all(user_id=current_user.id)
    if not isinstance(orders, list):
        orders = [orders]

    # orders_with_adv = []
    #
    # for order in orders:
    #     purchases = Purchase.get_all(order_id=order.id)
    #     advs = [Advert.get_all(id=purch.advert.id) for purch in purchases]
    #     orders_with_adv.append((order, advs))

    context = {
        'orders': orders[::-1],
        'categories': categories
    }

    return render_template('orders.html', **context)


@app.route('/orders/<int:page_id>')
@login_required
def order_page(page_id):
    order = Order.get_all(id=page_id)
    purchases = Purchase.get_all(order_id=order.id)
    if not isinstance(purchases, list):
        purchases = [purchases]
    advs = [Advert.get_all(id=purch.advert_id) for purch in purchases]

    context = {
        'order': order,
        'adverts': advs,
        'categories': categories
    }

    return render_template('order.html', **context)


if __name__ == '__main__':
    app.run()
