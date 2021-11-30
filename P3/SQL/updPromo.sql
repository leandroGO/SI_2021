ALTER TABLE customers
    ADD COLUMN IF NOT EXISTS promo numeric DEFAULT 0;

CREATE OR REPLACE FUNCTION updPromo() RETURNS TRIGGER
AS $$
BEGIN
    UPDATE orderdetail
    SET price = ROUND(products.price * (1 - customer.promo/100.0), 2)
    FROM orders, products
    WHERE orders.customerid = NEW.customerid
        AND orders.orderid = orderdetail.orderid
        AND orders.status IS NULL
        AND products.prod_id = orderdetail.prod_id;
END;
$$ LANGUAGE 'plpgsql';

DROP TRIGGER IF EXISTS tr_updPromo on customers;
CREATE TRIGGER tr_updPromo
AFTER UPDATE OF promo ON customers
    FOR EACH ROW EXECUTE PROCEDURE updPromo();
