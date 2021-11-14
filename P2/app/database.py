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
        _exceptionHandler(db_conn)

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
        _exceptionHandler(db_conn)

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
        _exceptionHandler(db_conn)

        return None

def db_movieInfo(id):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        query = f"SELECT movieid, movietitle, year FROM imdb_movies WHERE movieid = {id}"
        info = list(db_conn.execute(query))

        query = f"SELECT actorname FROM imdb_movies NATURAL JOIN imdb_actormovies NATURAL JOIN imdb_actors WHERE movieid = {id} ORDER BY creditsposition"
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
        _exceptionHandler(db_conn)

        return None


def db_productCheck(id):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        query = f"SELECT DISTINCT prod_id FROM inventory WHERE prod_id = {id} AND stock > 0"
        ret = len(list(db_conn.execute(query))) > 0

        db_conn.close()
        return ret
    except:
        _exceptionHandler(db_conn)

        return False

def db_add(user, id):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        query = f""
        db_conn.execute(query)

        db_conn.close()
        return
    except:
        _exceptionHandler(db_conn)

        return None

def db_sub(user, id):
    pass

def db_delete(user, id):
    pass


def db_getTitle(id):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        query = f"SELECT DISTINCT movietitle FROM imdb_movies NATURAL JOIN products WHERE prod_id = {id}"
        title = list(db_conn.execute(query))[0][0]

        db_conn.close()
        return title
    except:
        _exceptionHandler(db_conn)

        return None

def db_userCheck(email):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        query = f"SELECT DISTINCT email FROM customers WHERE email = '{email}'"
        ret = len(list(db_conn.execute(query))) > 0

        db_conn.close()
        return ret
    except:
        _exceptionHandler(db_conn)

        return False


def db_regUser(user_data):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        query = f"INSERT INTO customers(username, password, email, creditcard, address1, balance, loyalty) VALUES ('{user_data['name']}', '{user_data['password']}', '{user_data['email']}', '{user_data['tarjeta']}', '{user_data['direccion']}', {user_data['saldo']}, {user_data['puntos']})"
        db_conn.execute(query)

        db_conn.close()
        return
    except:
        _exceptionHandler(db_conn)

        return None

# Funciones auxiliares
def _exceptionHandler(db_conn):
    if db_conn is not None:
            db_conn.close()
    print("Exception in DB access:")
    print("-"*60)
    traceback.print_exc(file=sys.stderr)
    print("-"*60)