import json
from abc import ABC, abstractmethod
from collections import namedtuple

import bcrypt
import psycopg2


def get_id(model_name: str) -> int:
    with open('id_dict.json', 'r') as id_json:
        id_dict = json.load(id_json)
        id = id_dict[f'{model_name}']
        id_dict[f'{model_name}'] += 1
    with open('id_dict.json', 'w') as id_json:
        json.dump(id_dict, id_json)
    return id


UserTuple = namedtuple('UserTuple', 'name email password id')

AdvertTuple = namedtuple('AdvertTuple', 'title description category id user_id cost image_url')

OrderTuple = namedtuple('OrderTuple', 'user_id summa id')

PurchaseTuple = namedtuple('PurchaseTuple', 'advert_id order_id')

FavouriteTuple = namedtuple('FavouriteTuple', 'user_id advert_id')

CartTuple = namedtuple('CartTuple', 'user_id advert_id')


class DataBase(ABC):
    con = psycopg2.connect(
        dbname='avito',
        user='postgres',
        password='29853461',
        host='localhost',
        port='5432'
    )

    @abstractmethod
    def __init__(self):
        self.cur = self.con.cursor()

    @classmethod
    def get_all(cls, **kwargs):
        request = f"SELECT * FROM {cls.name}"
        if kwargs:
            request += f" WHERE "
            for key in kwargs:
                if key == 'id':
                    limitation = kwargs[key]
                else:
                    limitation = f"'{kwargs[key]}'"
                request += f"{key} = {limitation} AND "
            request = request[:-5] + ';'
        cur = cls.con.cursor()
        cur.execute(request)
        return cls.prepare_data(cur.fetchall())

    @classmethod
    def prepare_data(cls, list_of_tuples):
        list_of_objects = []
        for tup in list_of_tuples:
            list_of_objects.append(cls.named_tuple(*tup))
        if len(list_of_objects) == 1:
            return list_of_objects[0]
        return list_of_objects

    @abstractmethod
    def save(self, request):
        self.cur.execute(request)
        self.con.commit()


class User(DataBase):
    name = 'users'
    named_tuple = UserTuple

    def __init__(self, email, password, name=None):
        super().__init__()
        self.email = email
        if name:
            self.name = name
        else:
            self.name = email.split('@')[0]
        self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).hex()
        self.id = get_id('user')

    def save(self):
        super().save(
            f'''INSERT INTO users (name, email, password, id)
            VALUES ('{self.name}', '{self.email}', '{self.password}', {self.id});'''
        )

    @staticmethod
    def check_password(password, hash_password):
        return bcrypt.checkpw(password.encode(), bytes.fromhex(hash_password))


class Advert(DataBase):
    name = 'adverts'
    named_tuple = AdvertTuple

    def __init__(self, title, description, category, user_id, cost, image_url):
        super().__init__()
        self.title = title
        self.description = description
        self.category = category
        self.id = get_id('advert')
        self.user_id = user_id
        self.cost = cost
        self.image_url = image_url

    def save(self):
        super().save(
            f'''INSERT INTO advert (title, descrition, category, id, user_id, cost, image_url)
            VALUES  (
            '{self.title}',
            '{self.description}',
            '{self.category}',
            '{self.id}'),
            '{self.user_id}',
            '{self.cost}',
            '{self.image_url}';'''
        )


class Order(DataBase):
    name = 'orders'
    named_tuple = OrderTuple

    def __init__(self, user_id, summa):
        super().__init__()
        self.user_id = user_id
        self.summa = summa
        self.id = get_id('order')

    def save(self):
        super().save(
            f'''INSERT INTO orders (user_id, summa, id)
            VALUES ('{self.user_id}', '{self.summa}', '{self.id}');'''
        )


class Purchase(DataBase):
    name = 'purchases'
    named_tuple = PurchaseTuple

    def __init__(self, advert_id, order_id):
        super().__init__()
        self.advert_id = advert_id
        self.order_id = order_id

    def save(self):
        super().save(
            f'''INSERT INTO purchases (advert_id, order_id)
            VALUES ('{self.advert_id}', '{self.order_id}');'''
        )


class Favourite(DataBase):
    name = 'favourites'
    named_tuple = FavouriteTuple

    def __init__(self, user_id, advert_id):
        super().__init__()
        self.advert_id = advert_id
        self.user_id = user_id

    def save(self):
        super().save(
            f'''INSERT INTO favourites (advert_id, orders_id)
            VALUES ('{self.user_id}', '{self.advert_id}');'''
        )


class Cart(DataBase):
    name = 'cart'
    named_tuple = CartTuple

    def __init__(self, user_id, advert_id):
        super().__init__()
        self.advert_id = advert_id
        self.user_id = user_id

    def save(self):
        super().save(
            f'''INSERT INTO cart (advert_id, orders_id)
            VALUES ('{self.user_id}', '{self.advert_id}');'''
        )


if __name__ == '__main__':
    # user1 = User(name='Jojo', email='pro@pro.pro', password='jojo')
    # user2 = User(name='Han', email='han@han.han', password='han')
    # user1.save()
    # user2.save()
    jojo = User.get_all(name='Jojo')
    print(User.check_password('jojo', jojo.password))
