UPDATE orderdetail
	SET price = (
		SELECT DISTINCT ROUND(CAST(price/POWER(1.02, EXTRACT(years FROM CURRENT_DATE) - EXTRACT(years FROM orderdate)) AS numeric), 2)
		FROM products, orders
		WHERE orderdetail.prod_id = products.prod_id
		AND orders.orderid = orderdetail.orderid
	)