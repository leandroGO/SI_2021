SELECT COUNT(*)
FROM orders
WHERE status IS NULL;

SELECT COUNT(*)
FROM orders
WHERE status = 'Shipped';
