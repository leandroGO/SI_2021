CREATE OR REPLACE FUNCTION updOrders() RETURNS TRIGGER
AS $$
DECLARE
    affected_orderid orders.orderid%TYPE;
BEGIN
    IF TG_OP = 'DELETE' THEN
        affected_orderid = OLD.orderid;
    ELSE
        affected_orderid = NEW.orderid;
    END IF;

    UPDATE orders
    SET netamount = subquery.total,
        totalamount = ROUND(subquery.total * (1 + tax/100), 2)
    FROM (SELECT SUM(price*quantity) AS total
        FROM orderdetail
        WHERE orderdetail.orderid = affected_orderid
        GROUP BY orderdetail.orderid) AS subquery
    WHERE orders.orderid = affected_orderid;

    RETURN NULL;
END;
$$ LANGUAGE 'plpgsql';

DROP TRIGGER IF EXISTS tr_updOrders ON orderdetail;
CREATE TRIGGER tr_updOrders
AFTER INSERT OR UPDATE OR DELETE ON orderdetail
    FOR EACH ROW EXECUTE PROCEDURE updOrders();
