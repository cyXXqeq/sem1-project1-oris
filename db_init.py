import psycopg2
import json

con = psycopg2.connect(
    dbname='avito',
    user='postgres',
    password='29853461',
    host='localhost',
    port='5432'
)

cur = con.cursor()

if __name__ == '__main__':
    cur.execute(
        '''create table users
        (
            name     varchar(255),
            email    varchar(255) NOT NULL UNIQUE,
            salt     varchar      NOT NULL,
            password varchar      NOT NULL,
            id       integer      NOT NULL UNIQUE,
            PRIMARY KEY (id)
        );
        
        create table products
        (
            title       varchar(255) NOT NULL,
            description text         NOT NULL,
            cost        money        NOT NULL,
            category    varchar      NOT NULL,
            id          integer      NOT NULL UNIQUE,
            PRIMARY KEY (id)
        );
        
        create table orders
        (
            user_id integer NOT NULL,
            summa   money   NOT NULL,
            id      integer NOT NULL UNIQUE,
            PRIMARY KEY (id),
            CONSTRAINT fk_user
                FOREIGN KEY (user_id)
                    REFERENCES users (id)
                    ON DELETE CASCADE
        );
        
        create table purchases
        (
            product_id integer NOT NULL,
            order_id  integer NOT NULL,
            CONSTRAINT fk_product
                FOREIGN KEY (product_id)
                    REFERENCES products (id)
                    ON DELETE CASCADE,
            CONSTRAINT fk_orders
                FOREIGN KEY (order_id)
                    REFERENCES orders (id)
                    ON DELETE CASCADE
        );
        
        create table favourites
        (
            user_id    integer NOT NULL,
            product_id integer NOT NULL,
            CONSTRAINT fk_user
                FOREIGN KEY (user_id)
                    REFERENCES users (id)
                    ON DELETE CASCADE,
            CONSTRAINT fk_product
                FOREIGN KEY (product_id)
                    REFERENCES products (id)
                    ON DELETE CASCADE
        );
        
        create table basket
        (
            user_id    integer NOT NULL,
            product_id integer NOT NULL,
            CONSTRAINT fk_user
                FOREIGN KEY (user_id)
                    REFERENCES users (id)
                    ON DELETE CASCADE,
            CONSTRAINT fk_product
                FOREIGN KEY (product_id)
                    REFERENCES products (id)
                    ON DELETE CASCADE
        );'''
    )
    con.commit()

    id_dict = {
        'user': 0,
        'product': 0,
        'order': 0
    }
    with open('id_dict.json', 'w') as id_json:
        json.dump(id_dict, id_json)
