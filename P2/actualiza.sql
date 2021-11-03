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

/*--- inventory ---*/
ALTER TABLE inventory
    ADD CONSTRAINT inventory_prod_id_fkey
            FOREIGN KEY (prod_id)
            REFERENCES products(prod_id)
            ON DELETE CASCADE,
    ADD CONSTRAINT inventory_sales_positive CHECK (sales >= 0),
    ADD CONSTRAINT inventory_stock_positive CHECK (stock >= 0);

/*--- orderdetail ---*/
ALTER TABLE orderdetail
    DROP COLUMN price,
    ADD CONSTRAINT orderdetail_orderid_fkey
            FOREIGN KEY (orderid)
            REFERENCES orders(orderid)
            ON DELETE CASCADE,
    ADD CONSTRAINT orderdetail_prod_id_fkey
            FOREIGN KEY (prod_id)
            REFERENCES products(prod_id)
            ON DELETE CASCADE;

/*--- orders ---*/
CREATE TYPE order_status AS ENUM ('Paid', 'Processed', 'Shipped');

ALTER TABLE orders
    ADD CONSTRAINT orders_customerid_fkey
            FOREIGN KEY (customerid)
            REFERENCES customers(customerid)
            ON DELETE CASCADE,
    ALTER COLUMN status TYPE order_status USING status::order_status;

/* Only one order has status NULL per customer */
CREATE UNIQUE INDEX i_orders_one_null
    ON orders (customerid, (status IS NULL))
    WHERE status IS NULL;
