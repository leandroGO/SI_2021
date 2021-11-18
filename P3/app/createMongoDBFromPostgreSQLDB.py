# -*- coding: utf-8 -*-

import os
import sys, traceback, time

from sqlalchemy import create_engine
from pymongo import MongoClient

TOP_LIMIT = 400

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False)

# Crea la conexión con MongoDB
mongo_client = MongoClient()


# Extrae id y título de las TOP_LIMIT películas británicas más recientes
query = ("SELECT movieid, movietitle"
         "FROM imdb_moviecountries"
         "NATURAL JOIN imdb_movies"
         "WHERE country = 'UK'"
         f"ORDER BY year DESC LIMIT {TOP_LIMIT}")

try:
    db_conn = db_engine.connect()
    db_result = db_conn.execute(query)
    db_conn.close()
    movies = list(db_result)
except:
    _exceptionHandler(db_conn)
