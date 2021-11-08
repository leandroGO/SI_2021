/* Vista auxiliar */
CREATE OR REPLACE VIEW top_sales_per_year AS
    SELECT year, MAX(sales) as top_sales
    FROM imdb_movies
        NATURAL JOIN products
        NATURAL JOIN inventory
    GROUP BY imdb_movies.year;

CREATE OR REPLACE FUNCTION getTopSales(year1 INT, year2 INT, OUT Year INT, OUT
    Film CHAR, OUT sales bigint) RETURNS SETOF RECORD AS $$
BEGIN
    RETURN QUERY SELECT DISTINCT ON(imdb_movies.year, sales)
            imdb_movies.year,
            movietitle::CHAR(255),
            inventory.sales::bigint
    FROM imdb_movies
        NATURAL JOIN products
        NATURAL JOIN inventory
    WHERE imdb_movies.year >= year1
            AND imdb_movies.year <= year2
            AND inventory.sales = (SELECT top_sales
                         FROM top_sales_per_year AS tspy
                         WHERE tspy.year = imdb_movies.year)
    ORDER BY sales DESC;
END;
$$ LANGUAGE 'plpgsql';
