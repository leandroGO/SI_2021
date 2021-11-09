CREATE OR REPLACE FUNCTION getTopActors(genre character varying(32), OUT Actor character varying(128),
	OUT Num INT, OUT Debut INT, OUT Film character varying(255), OUT Director character varying(128)) RETURNS SETOF RECORD AS $$
BEGIN		
	RETURN QUERY SELECT actorname, frequence.Num::INT, frequence.Debut::INT, movietitle, directorname
	FROM imdb_actors NATURAL JOIN imdb_actormovies NATURAL JOIN (SELECT actorid, COUNT(*) AS Num, MIN(imdb_movies.year) as Debut
		FROM imdb_actors NATURAL JOIN imdb_actormovies NATURAL JOIN imdb_movies NATURAL JOIN imdb_moviegenres
		WHERE imdb_moviegenres.genre = getTopActors.genre
		GROUP BY actorid) AS frequence
	NATURAL JOIN imdb_movies NATURAL JOIN imdb_directormovies NATURAL JOIN imdb_directors
	WHERE frequence.Num >= 4 AND frequence.Debut = year
	ORDER BY frequence.Num DESC, frequence.Debut;
END;
$$ LANGUAGE 'plpgsql';