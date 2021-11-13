# -*- coding: utf-8 -*-

import os
import sys, traceback
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.sql import select

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False)
db_meta = MetaData(bind=db_engine)

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

        if genre is None:
            query = f"SELECT * FROM imdb_movies WHERE movietitle ILIKE '%%{keyword}%%'"
        else:
            query = f"SELECT * FROM imdb_movies NATURAL JOIN imdb_moviegenres WHERE movietitle ILIKE '%%{keyword}%%' AND genre = '{genre}'"
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

def movieInfo(id):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        query = f"SELECT movieid, movietitle, year FROM imdb_movies WHERE movieid = {id}"
        info = list(db_conn.execute(query))

        query = f"SELECT actorname FROM imdb_movies NATURAL JOIN imdb_actormovies NATURAL JOIN imdb_actors WHERE movieid = {id}"
        db_result = list(db_conn.execute(query))
        reparto = [actor[0] for actor in db_result]
        if len(reparto) >= 1:
            reparto = "; ".join(reparto)
        else:
            reparto = None

        query = f"SELECT genre FROM imdb_movies NATURAL JOIN imdb_moviegenres NATURAL JOIN imdb_genres WHERE movieid = {id}"
        db_result = list(db_conn.execute(query))
        generos = [genero[0] for genero in db_result]
        if len(generos) >= 1:
            generos = ", ".join(generos)
        else:
            generos = None

        query = f"SELECT directorname FROM imdb_movies NATURAL JOIN imdb_directormovies NATURAL JOIN imdb_directors WHERE movieid = {id}"
        db_result = list(db_conn.execute(query))
        directores = [director[0] for director in db_result]
        if len(directores) >= 1:
            directores = "; ".join(directores)
        else:
            directores = None

        query = f"SELECT prod_id, description, price FROM imdb_movies NATURAL JOIN products NATURAL JOIN inventory WHERE movieid = {id} AND stock > 0"
        precios = list(db_conn.execute(query))

        db_conn.close()
        return (info, reparto, generos, directores, precios)
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return None
