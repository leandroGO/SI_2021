CREATE OR REPLACE FUNCTION updInventoryAndCustomer() RETURNS TRIGGER
AS $$
DECLARE
    cart_prod RECORD;
    inventory_prod RECORD;
BEGIN
    IF OLD.status IS NOT NULL THEN    /* Is not a recently purchased cart */
        RETURN NULL;
    END IF;

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
        /*IF EXISTS (SELECT NULL
                    FROM inventory
                    WHERE inventory.prod_id = cart_prod.prod_id
                            AND stock < cart_prod.quantity) THEN*/
        IF inventory_prod.stock < cart_prod.quantity THEN
            RAISE EXCEPTION 'Not enough stock of %', cart_prod.prod_name;
        ELSIF inventory_prod.stock = cart_prod.quantity THEN
            /* TODO: crear alarma */
        END_IF;
    END LOOP;

    /* UPDATE inventory */

    DROP TABLE purchased_products;
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

DROP TRIGGER IF EXISTS tr_updInventoryAndCustomer;
CREATE TRIGGER tr_updInventoryAndCustomer
BEFORE UPDATE OF status ON orders
    FOR EACH ROW EXECUTE PROCEDURE updInventoryAndCustomer();
