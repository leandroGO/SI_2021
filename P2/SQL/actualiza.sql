/*--- imdb_actormovies ---*/
ALTER TABLE imdb_actormovies
    ADD CONSTRAINT imdb_actormovies_actorid_fkey
            FOREIGN KEY (actorid)
            REFERENCES imdb_actors(actorid)
            ON DELETE CASCADE,
    ADD CONSTRAINT imdb_actormovies_movieid_fkey
            FOREIGN KEY (movieid)
            REFERENCES imdb_movies(movieid)
            ON DELETE CASCADE,
    ADD CONSTRAINT imdb_actormovies_pkey PRIMARY KEY (actorid, movieid);

/*--- imdb_directormovies ---*/
ALTER TABLE imdb_directormovies
    DROP CONSTRAINT imdb_directormovies_pkey,
    ADD CONSTRAINT imdb_directormovies_pkey PRIMARY KEY (directorid, movieid);

/*--- imdb_movies ---*/
ALTER TABLE imdb_movies
    ALTER COLUMN year TYPE integer
        USING (LEFT(year, 4)::integer),
    DROP COLUMN movierelease;

/*--- inventory ---*/
ALTER TABLE inventory
    ADD CONSTRAINT inventory_prod_id_fkey
            FOREIGN KEY (prod_id)
            REFERENCES products(prod_id)
            ON DELETE CASCADE,
    ADD CONSTRAINT inventory_sales_positive CHECK (sales >= 0),
    ADD CONSTRAINT inventory_stock_positive CHECK (stock >= 0);

/*--- orderdetail ---*/
SELECT orderid, prod_id, SUM(quantity) AS quantity INTO new_orderdetail
FROM orderdetail
GROUP BY orderid, prod_id;

DROP TABLE orderdetail;

ALTER TABLE new_orderdetail RENAME TO orderdetail;

ALTER TABLE orderdetail
    ADD COLUMN price numeric,
    ADD CONSTRAINT orderdetail_orderid_fkey
            FOREIGN KEY (orderid)
            REFERENCES orders(orderid)
            ON DELETE CASCADE,
    ADD CONSTRAINT orderdetail_prod_id_fkey
            FOREIGN KEY (prod_id)
            REFERENCES products(prod_id)
            ON DELETE CASCADE,
    ADD CONSTRAINT orderdetail_pkey PRIMARY KEY (orderid, prod_id);

/*--- orders ---*/
CREATE TYPE order_status AS ENUM ('Paid', 'Processed', 'Shipped');

ALTER TABLE orders
    ADD CONSTRAINT orders_customerid_fkey
            FOREIGN KEY (customerid)
            REFERENCES customers(customerid)
            ON DELETE CASCADE,
    ALTER COLUMN status TYPE order_status USING status::order_status,
    ADD COLUMN points BOOLEAN DEFAULT FALSE;

/* Only one order has status NULL per customer */
CREATE UNIQUE INDEX i_orders_one_null
    ON orders (customerid, (status IS NULL))
    WHERE status IS NULL;

/*--- imdb_genres ---*/
SELECT DISTINCT genre INTO imdb_genres
FROM imdb_moviegenres;

ALTER TABLE imdb_genres
    ADD CONSTRAINT genres_pkey PRIMARY KEY (genre);

ALTER TABLE imdb_moviegenres
    ADD CONSTRAINT moviegenres_genre_fkey
        FOREIGN KEY (genre)
        REFERENCES imdb_genres(genre)
        ON DELETE CASCADE;

/*--- imdb_laguages ---*/
SELECT DISTINCT language, extrainformation INTO imdb_laguages
FROM imdb_movielanguages;

ALTER TABLE imdb_laguages
    ADD CONSTRAINT languages_pkey PRIMARY KEY (language, extrainformation);

ALTER TABLE imdb_movielanguages
    ADD CONSTRAINT movielanguages_language_fkey
        FOREIGN KEY (language, extrainformation)
        REFERENCES imdb_laguages(language, extrainformation)
        ON DELETE CASCADE;

/*--- imdb_country ---*/
SELECT DISTINCT country INTO imdb_countries
FROM imdb_moviecountries;

ALTER TABLE imdb_countries
    ADD CONSTRAINT countries_pkey PRIMARY KEY (country);

ALTER TABLE imdb_moviecountries
    ADD CONSTRAINT moviecoutries_country_fkey
        FOREIGN KEY (country)
        REFERENCES imdb_countries(country)
        ON DELETE CASCADE;

/*--- alerts ---*/
CREATE TABLE alerts (
    prod_id integer,
    alert_timestamp TIMESTAMP WITH TIME ZONE
);

ALTER TABLE alerts
    ADD CONSTRAINT alerts_product_fkey
        FOREIGN KEY (prod_id)
        REFERENCES inventory(prod_id)
        ON DELETE CASCADE,
    ADD CONSTRAINT alerts_pkey PRIMARY KEY (prod_id, alert_timestamp);

/*--- customers ---*/
ALTER TABLE customers
    ADD loyalty integer NOT NULL
        CONSTRAINT customer_loyalty_default
        DEFAULT (0),
    ADD balance numeric NULL,
    ADD CONSTRAINT customer_unique_email UNIQUE (email),
    ALTER COLUMN firstname DROP NOT NULL,
    ALTER COLUMN lastname DROP NOT NULL,
    ALTER COLUMN city DROP NOT NULL,
    ALTER COLUMN country DROP NOT NULL,
    ALTER COLUMN region DROP NOT NULL,
    ALTER COLUMN creditcardtype DROP NOT NULL,
    ALTER COLUMN creditcardexpiration DROP NOT NULL;


/*--- Serial sequences ---*/
/* imdb_actors */
SELECT pg_catalog.setval(
    pg_get_serial_sequence('imdb_actors', 'actorid'), MAX(actorid))
FROM imdb_actors;

/* imdb_directors */
SELECT pg_catalog.setval(
    pg_get_serial_sequence('imdb_directors', 'directorid'), MAX(directorid))
FROM imdb_directors;

/* imdb_movies */
SELECT pg_catalog.setval(
    pg_get_serial_sequence('imdb_movies', 'movieid'), MAX(movieid))
FROM imdb_movies;

/* customers */
SELECT pg_catalog.setval(
    pg_get_serial_sequence('customers', 'customerid'), MAX(customerid))
FROM customers;

/* orders */
SELECT pg_catalog.setval(
    pg_get_serial_sequence('orders', 'orderid'), MAX(orderid))
FROM orders;

/* products */
SELECT pg_catalog.setval(
    pg_get_serial_sequence('products', 'prod_id'), MAX(prod_id))
FROM products;

/*--- setCustomersBalance ---*/
CREATE OR REPLACE FUNCTION setCustomersBalance(IN initialBalance bigint)
    RETURNS void AS $$
    UPDATE customers
    SET balance = ROUND(CAST(random()*initialBalance AS numeric), 2);
$$ LANGUAGE SQL;

SELECT setCustomersBalance(100);

/*--- setPrice.sql ---*/
\ir SQL/setPrice.sql

/*--- setOrderAmount ---*/
\ir SQL/setOrderAmount.sql
SELECT setOrderAmount();

/*--- getTopSales ---*/
\ir SQL/getTopSales.sql

/*--- getTopActors ---*/
\ir SQL/getTopActors.sql

/*--- updOrders ---*/
\ir SQL/updOrders.sql

/*--- updInventoryAndCustomer ---*/
\ir SQL/updInventoryAndCustomer.sql
