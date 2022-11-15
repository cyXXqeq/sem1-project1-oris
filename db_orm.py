from abc import ABC, abstractmethod

import bcrypt
import psycopg2
from flask_login import UserMixin


class DataBase(ABC):
    con = psycopg2.connect(
        dbname='avito',
        user='postgres',
        password='29853461',
        host='localhost',
        port='5432'
    )

    @abstractmethod
    def __init__(self, *args):
        self.cur = self.con.cursor()

    @classmethod
    def get_all(cls, **kwargs):
        request = f"SELECT * FROM {cls.name}"
        if kwargs:
            request += f" WHERE "
            for key, value in kwargs.items():
                if key == 'id':
                    limitation = kwargs[key]
                else:
                    limitation = f"'{value}'"
                if limitation == "'not null'":
                    request += f"{key} IS NOT NULL AND "
                elif key == 'category' and value:
                    request += "category = %s AND "
                elif key == 'search' and value:
                    request += "(UPPER(title) LIKE UPPER(%s) OR UPPER(description) LIKE UPPER(%s)) AND "
                else:
                    if key == 'category':
                        continue
                    elif key == 'search':
                        continue
                    else:
                        request += f"{key} = {limitation} AND "
            request = request[:-5] + ';'
        try:
            cur = cls.con.cursor()
            if kwargs.get('category') and kwargs.get('search'):
                cur.execute(request, [kwargs['category']] + ['%' + kwargs['search'] + '%'] * 2)
            elif kwargs.get('category'):
                cur.execute(request, [kwargs['category']])
            elif kwargs.get('search'):
                cur.execute(request, ['%' + kwargs['search'] + '%'] * 2)
            else:
                cur.execute(request)
            return cls.prepare_data(cur.fetchall())
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def prepare_data(cls, list_of_tuples):
        list_of_objects = []
        for tup in list_of_tuples:
            list_of_objects.append(cls(*tup))
        if len(list_of_objects) == 1:
            return list_of_objects[0]
        return list_of_objects

    @abstractmethod
    def save(self, request, data):
        try:
            self.cur.execute(request, data)
            self.con.commit()
        except Exception as ex:
            print(ex)
            return False

    def update(self, **kwargs):
        try:
            fields = [kwarg[0] for kwarg in kwargs.items()]
            values = [kwarg[1] for kwarg in kwargs.items()]
            request = f"UPDATE {self.__class__.name} SET ("
            field_str = ""
            for field in fields:
                field_str += f"{field}, "
            request += field_str[:-2] + ") = (" + "%s, " * len(values)
            request = request[:-2] + f") WHERE id = {self.id}"
            self.cur.execute(request, values)
            self.con.commit()
        except Exception as ex:
            print(ex)
            return False


class DeleteMixin:
    def delete(self):
        try:
            self.cur.execute(f"DELETE FROM {self.__class__.name} WHERE id = %s", [self.id])
            self.con.commit()
        except Exception as ex:
            print(ex)
            return False


class User(DataBase, UserMixin, DeleteMixin):
    name = 'users'

    def __init__(self, email, password, name=None, image_url=None, admin_status=False, id=None, created_at=None):
        super().__init__()
        self.email = email
        if id is None:
            self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).hex()
        else:
            self.password = password
        if name:
            self.name = name
        else:
            self.name = email.split('@')[0]
        self.image_url = image_url
        self.admin_status = admin_status
        self.id = id
        self.created_at = created_at

    def save(self):
        if self.id:
            print('Cannot save existing object, use update function')
        else:
            request = "INSERT INTO users VALUES (%s, %s, %s, %s, %s);"
            data = [
                self.email,
                self.password,
                self.name,
                self.image_url,
                self.admin_status
            ]
            super().save(request, data)
            users = User.get_all()
            if isinstance(users, User):
                self.id = users.id
                self.created_at = users.created_at
            else:
                self.id = users[-1].id
                self.created_at = users[-1].created_at

    @staticmethod
    def check_password(password, hash_password):
        return bcrypt.checkpw(password.encode(), bytes.fromhex(hash_password))


class Advert(DataBase, DeleteMixin):
    name = 'adverts'

    def __init__(self, title, description, category, cost, image_url, user_id, id=None):
        super().__init__()
        self.title = title
        self.description = description
        self.category = category
        self.cost = cost
        self.image_url = image_url
        self.user_id = user_id
        self.id = id

    def save(self):
        if self.id:
            print('Cannot save existing object, use update function')
        else:
            request = "INSERT INTO adverts VALUES  (%s, %s, %s, %s, %s, %s);"
            data = [
                self.title,
                self.description,
                self.category,
                self.cost,
                self.image_url,
                self.user_id
            ]
            super().save(request, data)
            adverts = Advert.get_all()
            if isinstance(adverts, Advert):
                self.id = adverts.id
            else:
                self.id = adverts[-1].id


class Order(DataBase):
    name = 'orders'

    def __init__(self, summa, user_id, id=None):
        super().__init__()
        self.summa = summa
        self.user_id = user_id
        self.id = id

    def save(self):
        if self.id:
            print('Cannot save existing object, use update function')
        else:
            super().save("INSERT INTO orders VALUES (%s, %s);", [self.summa, self.user_id])
            orders = Order.get_all()
            if isinstance(orders, Order):
                self.id = orders.id
            else:
                self.id = orders[-1].id


class Purchase(DataBase):
    name = 'purchases'

    def __init__(self, advert_id, order_id):
        super().__init__()
        self.advert_id = advert_id
        self.order_id = order_id

    def save(self):
        super().save("INSERT INTO purchases VALUES (%s, %s);", [self.advert_id, self.order_id])


class Favorite(DataBase):
    name = 'favorites'

    def __init__(self, user_id, advert_id):
        super().__init__()
        self.user_id = user_id
        self.advert_id = advert_id

    def save(self):
        super().save("INSERT INTO favorites VALUES (%s, %s);", [self.user_id, self.advert_id])


class Cart(DataBase, DeleteMixin):
    name = 'cart'

    def __init__(self, user_id, advert_id, count=1):
        super().__init__()
        self.user_id = user_id
        self.advert_id = advert_id
        self.count = count

    def save(self):
        super().save("INSERT INTO cart VALUES (%s, %s, %s);", [self.user_id, self.advert_id, self.count])

# if __name__ == '__main__':
# user1 = User(name='Jojo', email='pro@pro.pro', password='jojo', admin_status=True)
# user2 = User(name='Han', email='han@han.han', password='han')
# user1.save()
# user2.save()
# jojo = User.get_all(name='Jojo')
# print(User.check_password('jojo', jojo.password))
# user3 = User(email='test@test.test', password='test')
# user3.save()
# print(User.check_password('test', User.get_all(email='test@test.test').password))
# adverts = Advert.get_all()
# for adv in adverts:
#     print(adv.title, adv.description, adv.category, adv.cost, adv.image_url, adv.user_id, adv.id, "----------", sep='\n')
