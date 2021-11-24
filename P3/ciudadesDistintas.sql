SELECT COUNT(*)
FROM (SELECT DISTINCT city
	FROM customers NATURAL JOIN
		orders
	WHERE creditcardtype = 'VISA' AND
		to_char(orderdate, 'YYYYMM') = '201604') AS distinctCities