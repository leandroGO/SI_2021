BEGIN;

/* Explain Plan previo a la creación del índice */
\echo *** Plan previo al indice ***
EXPLAIN SELECT COUNT(*)
FROM orders
WHERE status IS NULL;

EXPLAIN SELECT COUNT(*)
FROM orders
WHERE status = 'Shipped';

/* Explain Plan tras la creación del índice */
\echo *** Plan previo a las estadisticas ***
CREATE INDEX index_orders_status ON orders(status);

EXPLAIN SELECT COUNT(*)
FROM orders
WHERE status IS NULL;

EXPLAIN SELECT COUNT(*)
FROM orders
WHERE status = 'Shipped';

/* Explain Plan tras generación de estadísticas */
\echo *** Plan tras estadisticas ***
ANALYZE orders;

EXPLAIN SELECT COUNT(*)
FROM orders
WHERE status IS NULL;

EXPLAIN SELECT COUNT(*)
FROM orders
WHERE status = 'Shipped';

EXPLAIN SELECT COUNT(*)
FROM orders
WHERE status = 'Paid';

EXPLAIN SELECT COUNT(*)
FROM orders
WHERE status = 'Processed';

ROLLBACK;   /* Vuelve al estado inicial */
