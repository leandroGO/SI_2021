UPDATE orderdetail
SET price =
    ROUND((products.price * POWER(1.02, EXTRACT(year FROM orders.orderdate) -
                EXTRACT(year FROM CURRENT_DATE)))::numeric, 2)
FROM products, orders
WHERE orderdetail.prod_id = products.prod_id
    AND orderdetail.orderid = orders.orderid;
