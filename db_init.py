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
            email    varchar(255) NOT NULL UNIQUE,
            password varchar      NOT NULL,
            name     varchar(255),
            id       integer      NOT NULL UNIQUE,
            PRIMARY KEY (id)
        );
        
        create table adverts
        (
            title       varchar(255)     NOT NULL,
            description text             NOT NULL,
            category    varchar          NOT NULL,
            cost        double precision NOT NULL,
            image_url   text,
            user_id     integer          NOT NULL,
            id          integer          NOT NULL UNIQUE,
            PRIMARY KEY (id),
            CONSTRAINT fk_user
                FOREIGN KEY (user_id)
                    REFERENCES users (id)
                    ON DELETE CASCADE 
        );
        
        create table orders
        (
            summa   money   NOT NULL,
            user_id integer NOT NULL,
            id      integer NOT NULL UNIQUE,
            PRIMARY KEY (id),
            CONSTRAINT fk_user
                FOREIGN KEY (user_id)
                    REFERENCES users (id)
                    ON DELETE CASCADE
        );
        
        create table purchases
        (
            advert_id integer NOT NULL,
            order_id  integer NOT NULL,
            CONSTRAINT fk_advert
                FOREIGN KEY (advert_id)
                    REFERENCES adverts (id)
                    ON DELETE CASCADE,
            CONSTRAINT fk_orders
                FOREIGN KEY (order_id)
                    REFERENCES orders (id)
                    ON DELETE CASCADE
        );
        
        create table favourites
        (
            user_id    integer NOT NULL,
            advert_id integer NOT NULL,
            CONSTRAINT fk_user
                FOREIGN KEY (user_id)
                    REFERENCES users (id)
                    ON DELETE CASCADE,
            CONSTRAINT fk_advert
                FOREIGN KEY (advert_id)
                    REFERENCES adverts (id)
                    ON DELETE CASCADE
        );
        
        create table cart
        (
            user_id    integer NOT NULL,
            advert_id integer NOT NULL,
            CONSTRAINT fk_user
                FOREIGN KEY (user_id)
                    REFERENCES users (id)
                    ON DELETE CASCADE,
            CONSTRAINT fk_advert
                FOREIGN KEY (advert_id)
                    REFERENCES adverts (id)
                    ON DELETE CASCADE
        );'''
    )
    con.commit()

    id_dict = {
        'user': 0,
        'advert': 0,
        'order': 0
    }
    with open('id_dict.json', 'w') as id_json:
        json.dump(id_dict, id_json)
