CREATE OR REPLACE FUNCTION updInventoryAndCustomer() RETURNS TRIGGER
AS $$
DECLARE
    points_per_euro INT;
    loyalty_percent NUMERIC;
BEGIN
    points_per_euro = 100;
    loyalty_percent = 0.05;

    IF OLD.status IS NOT NULL THEN    /* Is not a recently purchased cart */
        RETURN NULL;
    END IF;

    /* Update tables */
    UPDATE inventory
    SET stock = stock - quantity,
        sales = sales + quantity
    FROM orderdetail
    WHERE orderdetail.prod_id = inventory.prod_id
        AND orderdetail.orderid = NEW.orderid;

    INSERT INTO alerts(prod_id, alert_timestamp)
    SELECT prod_id, CURRENT_TIMESTAMP
    FROM inventory
        NATURAL JOIN orderdetail
    WHERE orderdetail.orderid = NEW.orderid
        AND stock = 0;

    IF NEW.points THEN
        UPDATE customers
        SET loyalty = loyalty - NEW.totalamount * points_per_euro
        WHERE NEW.customerid = customerid;
    ELSE
        UPDATE customers
        SET balance = balance - NEW.totalamount
        WHERE NEW.customerid = customerid;
    END IF;

    UPDATE customers
    SET loyalty = (loyalty + NEW.totalamount * loyalty_percent * points_per_euro)::INT
    WHERE NEW.customerid = customerid;

    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

DROP TRIGGER IF EXISTS tr_updInventoryAndCustomer ON orders;
CREATE TRIGGER tr_updInventoryAndCustomer
BEFORE UPDATE OF status ON orders
    FOR EACH ROW EXECUTE PROCEDURE updInventoryAndCustomer();
