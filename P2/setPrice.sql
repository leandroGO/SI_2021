UPDATE orderdetail
	SET price = products.price / POWER(1.02, EXTRACT(years FROM CURRENT_DATE) - EXTRACT(years FROM orders.orderdate))
	FROM orderdetail O2
	NATURAL JOIN orders
	INNER JOIN products ON (
		O2.prod_id = products.prod_id
	)
	WHERE o2.orderid = 1;