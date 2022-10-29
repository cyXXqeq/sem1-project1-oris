import psycopg2
from os import urandom
from hashlib import pbkdf2_hmac
import json


def get_id(model_name: str) -> int:
    with open('id_dict.json', 'r') as id_json:
        id_dict = json.load(id_json)
        id = id_dict[f'{model_name}']
        id_dict[f'{model_name}'] += 1
    with open('id_dict.json', 'w') as id_json:
        json.dump(id_dict, id_json)
    return id


class DataBase:
    def __init__(self):
        self.con = psycopg2.connect(
            dbname='avito',
            user='postgres',
            password='29853461',
            host='localhost',
            port='5432'
        )
        self.cur = self.con.cursor()


class User(DataBase):
    def __init__(self, email, password, name=None):
        super().__init__()
        self.email = email
        if name:
            self.name = name
        else:
            self.name = email.split('@')[0]
        self.salt = urandom(32)
        self.password = pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            self.salt,
            100000
        )
        self.id = get_id('user')

    def save(self):
        self.cur.execute(
            f'''INSERT INTO users (name, email, salt, password, id)
            VALUES ('{self.name}', '{self.email}', '{self.salt}' '{self.password}', '{self.id}')'''
        )
        self.con.commit()


class Products(DataBase):
    def __init__(self, title, description, cost, category):
        super().__init__()
        self.title = title
        self.description = description
        self.cost = cost
        self.category = category
        self.id = get_id('product')

    def save(self):
        self.cur.execute(
            f'''INSERT INTO products (title, descrition, cost, category, id)
            VALUES  ('{self.title}', '{self.description}', '{self.cost}', '{self.category}', '{self.id}')'''
        )
        self.con.commit()


class Orders(DataBase):
    def __init__(self, user_id, summa):
        super().__init__()
        self.user_id = user_id
        self.summa = summa
        self.id = get_id('order')

    def save(self):
        self.cur.execute(
            f'''INSERT INTO orders (user_id, summa, id)
            VALUES ('{self.user_id}', '{self.summa}', '{self.id}')'''
        )
        self.con.commit()


class Purchases(DataBase):
    def __init__(self, product_id, orders_id):
        super().__init__()
        self.product_id = product_id
        self.orders_id = orders_id

    def save(self):
        self.cur.execute(
            f'''INSERT INTO purchases (product_id, orders_id)
            VALUES ('{self.product_id}', '{self.orders_id}')'''
        )
        self.con.commit()


class Favourites(DataBase):
    def __init__(self, user_id, product_id):
        super().__init__()
        self.product_id = product_id
        self.user_id = user_id

    def save(self):
        self.cur.execute(
            f'''INSERT INTO favourites (product_id, orders_id)
            VALUES ('{self.user_id}', '{self.product_id}')'''
        )
        self.con.commit()


class Basket(DataBase):
    def __init__(self, user_id, product_id):
        super().__init__()
        self.product_id = product_id
        self.user_id = user_id

    def save(self):
        self.cur.execute(
            f'''INSERT INTO basket (product_id, orders_id)
            VALUES ('{self.user_id}', '{self.product_id}')'''
        )
        self.con.commit()
