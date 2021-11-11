CREATE OR REPLACE FUNCTION updInventoryAndCustomer() RETURNS TRIGGER
AS $$
DECLARE
    cart_prod RECORD;
    inventory_prod RECORD;
    cust RECORD;
    points_per_euro INT;
BEGIN
    points_per_euro = 100;

    IF OLD.status IS NOT NULL THEN    /* Is not a recently purchased cart */
        RETURN NULL;
    END IF;

    /* Check balance or loyalty points are enough */
    cust = (SElECT *
                FROM customers
                WHERE customers.customerid = NEW.customerid);
    IF NEW.points THEN
        IF cust.loyalty < NEW.totalamount * points_per_euro THEN
            RAISE EXCEPTION 'Not enough loyalty points';
        END IF;
    ELSE
        IF cust.balance < NEW.totalamount THEN
            RAISE EXCEPTION 'Not enough funds in account';
        END IF;
    END IF;

    /* Check inventory stock */
    DROP TABLE IF EXISTS purchased_products;
    CREATE TABLE purchased_products AS
    SELECT prod_id,
        quantity,
        movietitle || ' ('|| products.description || ')' AS prod_name
    FROM orderdetail
        INNER JOIN products ON (orderdetail.prod_id = products.prod_id)
        INNER JOIN imdb_movies ON (products.movieid = imdb_movies.movieid)
    WHERE orderdetail.orderid = NEW.orderid;

    FOR cart_prod IN purchased_products LOOP
        inventory_prod = (SELECT *
                            FROM inventory
                            WHERE inventory.prod_id = cart_prod.prod_id);
        IF inventory_prod.stock < cart_prod.quantity THEN
            RAISE EXCEPTION 'Not enough stock of %', cart_prod.prod_name;
        ELSIF inventory_prod.stock = cart_prod.quantity THEN
            INSERT INTO alerts(prod_id, alert_date, alert_time)
            VAlUES (cart_prod.prod_id, CURRENT_DATE, LOCALTIME);
        END_IF;
    END LOOP;

    /* Update tables */
    UPDATE inventory
    SET stock = stock - quantity,
        sales = sales + quantity
    FROM purchased_products
    WHERE purchased_products.prod_id = inventory.prod_id;

    IF NEW.points THEN
        /* Update loyalty */
    ELSE
        /* Update balance */
    END IF;


    DROP TABLE purchased_products;
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

DROP TRIGGER IF EXISTS tr_updInventoryAndCustomer ON orders;
CREATE TRIGGER tr_updInventoryAndCustomer
BEFORE UPDATE OF status ON orders
    FOR EACH ROW EXECUTE PROCEDURE updInventoryAndCustomer();
