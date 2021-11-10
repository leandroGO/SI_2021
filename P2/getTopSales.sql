CREATE OR REPLACE FUNCTION getTopSales(year1 INT, year2 INT, OUT Year INT, OUT
    Film CHAR, OUT sales bigint) RETURNS SETOF RECORD AS $$
DECLARE
    min_year INT;
    max_year INT;
BEGIN
    min_year := LEAST(year1, year2);
    max_year := GREATEST(year1, year2);
    DROP TABLE IF EXISTS getTopSalesResults;
    CREATE TABLE getTopSalesResults (
        movieid INT,
        Year INT,
        sales bigint
    );

    WHILE min_year <= max_year LOOP
        DROP TABLE IF EXISTS getTopSalesAux;
        CREATE TABLE getTopSalesAux AS
        SELECT movieid, SUM(quantity) as total_sales
        FROM orders
        INNER JOIN orderdetail ON (orders.orderid = orderdetail.orderid)
        INNER JOIN products ON (orderdetail.prod_id = products.prod_id)
        WHERE EXTRACT(year FROM orderdate) = min_year
        GROUP BY movieid;

        INSERT INTO getTopSalesResults
        SELECT movieid, min_year AS Year, total_sales AS sales
        FROM getTopSalesAux
        WHERE total_sales = (SELECT MAX(total_sales) FROM getTopSalesAux);

        min_year := min_year + 1;
    END LOOP;

    RETURN QUERY SELECT DISTINCT ON(getTopSalesResults.Year, getTopSalesResults.sales)
    getTopSalesResults.Year,
    movietitle::CHAR(255),
    getTopSalesResults.sales
    FROM getTopSalesResults
    INNER JOIN imdb_movies ON (getTopSalesResults.movieid = imdb_movies.movieid)
    ORDER BY getTopSalesResults.sales DESC;

    DROP TABLE getTopSalesAux;
    DROP TABLE getTopSalesResults;
END;
$$ LANGUAGE 'plpgsql';
