/* imdb_actormovies */
ALTER TABLE imdb_actormovies
    ADD CONSTRAINT imdb_actormovies_actorid_fkey
        FOREIGN KEY (actorid)
        REFERENCES imdb_actors(actorid)
        ON DELETE CASCADE;

ALTER TABLE imdb_actormovies
    ADD CONSTRAINT imdb_actormovies_movieid_fkey
        FOREIGN KEY (movieid)
        REFERENCES imdb_movies(movieid)
        ON DELETE CASCADE;

ALTER TABLE imdb_actormovies
    ADD CONSTRAINT imdb_actormovies_pkey
        PRIMARY KEY (actorid, movieid);
