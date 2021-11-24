create or replace function dateFormat(dateField date)
returns
	char(6)
AS $$
	SELECT to_char(dateField, 'YYYYMM')
$$ LANGUAGE sql IMMUTABLE;

CREATE INDEX indice on orders (dateFormat(orderdate))

SELECT COUNT(*)
FROM (SELECT DISTINCT city
	FROM customers NATURAL JOIN
		orders
	WHERE creditcardtype = 'VISA' AND
		to_char(orderdate, 'YYYYMM') = '201604') AS distinctCities