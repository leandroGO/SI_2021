BEGIN;

/* Explain Plan previo a la creación del índice */
\echo *** Plan previo al indice ***
EXPLAIN SELECT COUNT(*)
FROM (SELECT DISTINCT city
    FROM customers
        NATURAL JOIN orders
    WHERE creditcardtype = 'VISA' AND
        to_char(orderdate, 'YYYYMM') = '201604') AS distinctCities;


CREATE OR REPLACE FUNCTION dateFormat(dateField DATE)
RETURNS
    CHAR(6)
AS $$
    SELECT to_char(dateField, 'YYYYMM')
$$ LANGUAGE SQL IMMUTABLE;

/* Explain Plan tras la creación del índice */
\echo *** Plan tras la creación del índice ***
CREATE INDEX index_orders_yearmonth ON orders (dateFormat(orderdate));

EXPLAIN SELECT COUNT(*)
FROM (SELECT DISTINCT city
    FROM customers
        NATURAL JOIN orders
    WHERE creditcardtype = 'VISA' AND
        dateFormat(orderdate) = '201604') AS distinctCities;

ROLLBACK;   /* Vuelve al estado inicial */
