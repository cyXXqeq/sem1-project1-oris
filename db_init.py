import psycopg2

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
               email        varchar(255) NOT NULL UNIQUE,
               password     varchar      NOT NULL,
               name         varchar(255),
               image_url    text,
               admin_status bool default false,
               id           serial       NOT NULL UNIQUE,
               created_at   date default current_date,
               PRIMARY KEY (id)
           );
           
           create table adverts
           (
               title       varchar(255)     NOT NULL,
               description text             NOT NULL,
               category    varchar          NOT NULL,
               cost        double precision NOT NULL,
               image_url   text,
               user_id     integer,
               id          serial           NOT NULL UNIQUE,
               PRIMARY KEY (id),
               CONSTRAINT fk_user
                   FOREIGN KEY (user_id)
                       REFERENCES users (id)
                       ON DELETE SET NULL
           );
           
           create table orders
           (
               summa   double precision NOT NULL,
               user_id integer          NOT NULL,
               id      serial           NOT NULL UNIQUE,
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
                       REFERENCES adverts (id),
               CONSTRAINT fk_orders
                   FOREIGN KEY (order_id)
                       REFERENCES orders (id)
                       ON DELETE CASCADE
           );
           
           create table favorites
           (
               user_id   integer NOT NULL,
               advert_id integer NOT NULL,
               CONSTRAINT fk_user
                   FOREIGN KEY (user_id)
                       REFERENCES users (id)
                       ON DELETE CASCADE,
               CONSTRAINT fk_advert
                   FOREIGN KEY (advert_id)
                       REFERENCES adverts (id)
           );
           
           create table cart
           (
               user_id   integer NOT NULL,
               advert_id integer NOT NULL,
               CONSTRAINT fk_user
                   FOREIGN KEY (user_id)
                       REFERENCES users (id)
                       ON DELETE CASCADE,
               CONSTRAINT fk_advert
                   FOREIGN KEY (advert_id)
                       REFERENCES adverts (id)
           );'''
    )
    con.commit()
