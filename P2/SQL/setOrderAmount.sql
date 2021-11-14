CREATE OR REPLACE FUNCTION setOrderAmount() RETURNS void AS $$
    UPDATE orders
    SET netamount = subquery.total,
        totalamount = ROUND(subquery.total * (1 + tax/100), 2)
    FROM (SELECT orderdetail.orderid, SUM(price*quantity) AS total
        FROM orderdetail
        GROUP BY orderdetail.orderid) AS subquery
    WHERE subquery.orderid = orders.orderid
            AND netamount IS NULL
            AND totalamount IS NULL;
$$ LANGUAGE SQL;
