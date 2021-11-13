CREATE OR REPLACE FUNCTION getTopActors(genre character varying(32),
    OUT Actor CHAR, OUT Num INT, OUT Debut INT, OUT Film CHAR,
    OUT Director CHAR) RETURNS SETOF RECORD AS $$
DECLARE
   target_genre ALIAS FOR genre;
BEGIN
   DROP TABLE IF EXISTS actor_genre;
   CREATE TABLE actor_genre AS
   SELECT actorid, COUNT(movieid) as Num, MIN(imdb_movies.year) as Debut
   FROM imdb_movies
       NATURAL JOIN imdb_actormovies
       NATURAL JOIN imdb_moviegenres
   WHERE imdb_moviegenres.genre = target_genre
   GROUP BY actorid;

   RETURN QUERY SELECT
       actorname::CHAR(32),
       actor_genre.Num::INT,
       actor_genre.Debut::INT,
       movietitle::CHAR(255),
       directorname::CHAR(128)
   FROM imdb_movies
       NATURAL JOIN imdb_actormovies
       NATURAL JOIN imdb_actors
       NATURAL JOIN actor_genre
       INNER JOIN imdb_directormovies ON imdb_directormovies.movieid = imdb_movies.movieid
       NATURAL JOIN imdb_directors
   WHERE actor_genre.Num > 4
       AND actor_genre.Debut = imdb_movies.year
   ORDER BY Num DESC;

   DROP TABLE actor_genre;
END;
$$ LANGUAGE 'plpgsql';
