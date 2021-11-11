# -*- coding: utf-8 -*-

import os
import sys, traceback
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.sql import select

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False)
db_meta = MetaData(bind=db_engine)
# cargar una tabla
db_table_movies = Table('imdb_movies', db_meta, autoload=True, autoload_with=db_engine)

def db_movieList():
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        #Tomaoms 20 peliculas de la BD
        query = "SELECT * FROM imdb_movies ORDER BY year DESC LIMIT 25"
        db_result = db_conn.execute(query)

        db_conn.close()
        return list(db_result)
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return None

def db_genres():
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        query = "SELECT genre from imdb_genres"
        db_result = db_conn.execute(query)

        db_conn.close()
        return [genre[0] for genre in list(db_result)]
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return None

def db_search(keyword, genre):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()
        print(keyword)

        if genre is None:
            query = f"SELECT * FROM imdb_movies WHERE movietitle ILIKE '%{keyword}%'"
        else:
            query = f"SELECT * FROM imdb_movies NATURAL JOIN imdb_moviegenres WHERE movietitle ILIKE '%{keyword}%' AND genre = '{genre}'"
        db_result = db_conn.execute(query)

        db_conn.close()
        return list(db_result)
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return None

