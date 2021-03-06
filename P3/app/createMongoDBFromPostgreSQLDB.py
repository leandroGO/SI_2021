# -*- coding: utf-8 -*-

import sys
import traceback
import re

from sqlalchemy import create_engine
from sqlalchemy import Table, MetaData, text, desc
from sqlalchemy.sql import select
from sqlalchemy.exc import SQLAlchemyError
from pymongo import MongoClient

TOP_LIMIT = 400
MAX_TOP_RELATED = 10
MAX_RELATED = 10


def run_query(db_engine, query, movieid):
    try:
        db_conn = db_engine.connect()
        db_result = db_conn.execute(query, movieid=movieid)
        db_conn.close()
    except SQLAlchemyError:
        _exceptionHandler(db_conn)
    return db_result


def _exceptionHandler(db_conn):
    if db_conn is not None:
        db_conn.close()
    print("Exception in DB access:")
    print("-"*60)
    traceback.print_exc(file=sys.stderr)
    print("-"*60)


# Extract ---------------------------------------------------------------------
print("Extracting data from PostgreSQL DB...", end='')
# Configura el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1",
                          echo=False)
db_meta = MetaData(bind=db_engine)

# Crea algunas tablas de la base relacional
db_movies = Table('imdb_movies', db_meta, autoload=True,
                  autoload_with=db_engine)
db_moviecountries = Table('imdb_moviecountries', db_meta, autoload=True,
                          autoload_with=db_engine)
db_moviegenres = Table('imdb_moviegenres', db_meta, autoload=True,
                       autoload_with=db_engine)
db_directors = Table('imdb_directors', db_meta, autoload=True,
                     autoload_with=db_engine)
db_directormovies = Table('imdb_directormovies', db_meta, autoload=True,
                          autoload_with=db_engine)
db_actors = Table('imdb_actors', db_meta, autoload=True,
                  autoload_with=db_engine)
db_actormovies = Table('imdb_actormovies', db_meta, autoload=True,
                       autoload_with=db_engine)

# Extrae id, título y año de las TOP_LIMIT películas británicas más recientes
query = (select([db_movies.c.movieid,
                 db_movies.c.movietitle.label('title'),
                 db_movies.c.year])
         .select_from(db_movies.join(db_moviecountries))
         .where(text("country = 'UK'"))
         .order_by(desc(db_movies.c.year))
         .limit(TOP_LIMIT))
try:
    db_conn = db_engine.connect()
    db_result = db_conn.execute(query)
    db_conn.close()
except SQLAlchemyError:
    _exceptionHandler(db_conn)
movies = [r._asdict() for r in db_result]

# Extrae la información restante (géneros, directores, actores)
q_genres = select([db_moviegenres.c.genre]).where(text("movieid = :movieid"))
q_directors = (select([db_directors.c.directorname])
               .select_from(db_directors.join(db_directormovies))
               .where(text("movieid = :movieid")))
q_actors = (select([db_actors.c.actorname])
            .select_from(db_actors.join(db_actormovies,
                         db_actors.c.actorid == db_actormovies.c.actorid))
            .where(text("movieid = :movieid"))
            .order_by(db_actormovies.c.creditsposition))
for movie in movies:
    movie['title'] = re.sub(r'\s\(.*\)$', '', movie['title'])
    movie['year'] = int(movie['year'])

    db_result = run_query(db_engine, q_genres, movie['movieid'])
    movie['genres'] = [g for g, in db_result]

    db_result = run_query(db_engine, q_directors, movie['movieid'])
    movie['directors'] = [d for d, in db_result]

    db_result = run_query(db_engine, q_actors, movie['movieid'])
    movie['actors'] = [a for a, in db_result]
print("OK")

# Transform -------------------------------------------------------------------
print("Transforming data...", end='')
# Encuentra las películas más relacionadas del top 400 UK
# Observación: el diccionario está ordenado por year desc
for m1 in movies:
    m1['most_related_movies'] = []
    for m2 in movies:
        if m1 != m2 and set(m1['genres']) == set(m2['genres']):
            m1['most_related_movies'].append({'title': m2['title'],
                                              'year': m2['year']})
        if len(m1['most_related_movies']) == MAX_TOP_RELATED:
            break

# Encuentra las películas relacionadas del top 400 UK
for m1 in movies:
    m1['related_movies'] = []
    num_genres = len(m1['genres'])
    for m2 in movies:
        common = set(m1['genres']).intersection(set(m2['genres']))
        if num_genres/2 <= len(common) < num_genres/2 + 1:
            m1['related_movies'].append({'title': m2['title'],
                                         'year': m2['year']})

        if len(m1['related_movies']) == MAX_RELATED:
            break
print("OK")

# Load ------------------------------------------------------------------------
print("Loading data into MongoDB...", end='')
# Crea la conexión con MongoDB
mongo_client = MongoClient()
si1_db = mongo_client.si1

# Carga los documentos de movies en la colección topUK
si1_db.topUK.drop()
si1_db.topUK.insert_many(movies)

mongo_client.close()
print("OK")
