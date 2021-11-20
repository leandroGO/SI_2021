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

        # Tomamos 25 peliculas de la BD
        query = ("SELECT * FROM imdb_movies ORDER BY year DESC LIMIT 25")
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

        query = ("SELECT genre FROM imdb_genres")
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
            query = ("SELECT * "
                     "FROM imdb_movies "
                     f"WHERE movietitle ILIKE '%%{keyword}%%'")
        else:
            query = (f"SELECT * "
                     "FROM imdb_movies "
                     "NATURAL JOIN imdb_moviegenres "
                     f"WHERE movietitle ILIKE '%%{keyword}%%' "
                     f"AND genre = '{genre}'")
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

        query = ("SELECT movieid, movietitle, year "
                 "FROM imdb_movies "
                 f"WHERE movieid = {id}")
        info = list(db_conn.execute(query))

        query = ("SELECT actorname "
                 "FROM imdb_movies "
                 "NATURAL JOIN imdb_actormovies "
                 "NATURAL JOIN imdb_actors "
                 f"WHERE movieid = {id} "
                 "ORDER BY creditsposition")
        db_result = list(db_conn.execute(query))
        reparto = [actor[0] for actor in db_result]
        if len(reparto) >= 1:
            reparto = "; ".join(reparto)
        else:
            reparto = None

        query = ("SELECT genre "
                 "FROM imdb_movies "
                 "NATURAL JOIN imdb_moviegenres "
                 "NATURAL JOIN imdb_genres "
                 f"WHERE movieid = {id}")
        db_result = list(db_conn.execute(query))
        generos = [genero[0] for genero in db_result]
        if len(generos) >= 1:
            generos = ", ".join(generos)
        else:
            generos = None

        query = ("SELECT directorname "
                 "FROM imdb_movies "
                 "NATURAL JOIN imdb_directormovies "
                 "NATURAL JOIN imdb_directors "
                 f"WHERE movieid = {id}")
        db_result = list(db_conn.execute(query))
        directores = [director[0] for director in db_result]
        if len(directores) >= 1:
            directores = "; ".join(directores)
        else:
            directores = None

        query = ("SELECT prod_id, description, price "
                 "FROM imdb_movies "
                 "NATURAL JOIN products "
                 "NATURAL JOIN inventory "
                 f"WHERE movieid = {id} AND stock > 0")
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

        query = ("SELECT DISTINCT prod_id "
                 "FROM inventory "
                 f"WHERE prod_id = {id} AND stock > 0")
        ret = len(list(db_conn.execute(query))) > 0

        db_conn.close()
        return ret
    except:
        _exceptionHandler(db_conn)

        return False

def db_add(email, id, quantity):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        query = ("SELECT orders.orderid "
                 "FROM customers "
                 "NATURAL JOIN orders "
                 "NATURAL JOIN orderdetail "
                 f"WHERE email = '{email}' "
                 "AND status IS NULL "
                 f"AND prod_id = {id}")
        db_result = list(db_conn.execute(query))

        if len(db_result) > 0:
            query = ("UPDATE orderdetail "
                     f"SET quantity = quantity + {quantity}"
                     f"WHERE orderid = {db_result[0][0]} AND prod_id = {id}")
        else:
            query = ("SELECT orders.orderid "
                     "FROM customers "
                     "NATURAL JOIN orders "
                     f"WHERE email = '{email}' AND status IS NULL")
            orderid = list(db_conn.execute(query))[0][0]
            query = ("INSERT INTO orderdetail(orderid, prod_id, quantity) "
                     f"VALUES ({orderid}, {id}, {quantity})")

        db_conn.execute(query)

        db_conn.close()
        return None
    except:
        _exceptionHandler(db_conn)

        return None

def db_sub(email, id):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        query = ("SELECT orders.orderid "
                 "FROM customers "
                 "NATURAL JOIN orders "
                 "NATURAL JOIN orderdetail "
                 f"WHERE email = '{email}' AND status IS NULL "
                 f"AND prod_id = {id} AND quantity > 1")
        db_result = list(db_conn.execute(query))

        if len(db_result) > 0:
            query = ("UPDATE orderdetail "
                     "SET quantity = quantity - 1 "
                     f"WHERE orderid = {db_result[0][0]} AND prod_id = {id}")
            db_conn.execute(query)

        db_conn.close()
        return None
    except:
        _exceptionHandler(db_conn)

        return None

def db_delete(email, id):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        query = ("SELECT orders.orderid "
                 "FROM customers "
                 "NATURAL JOIN orders "
                 "NATURAL JOIN orderdetail "
                 f"WHERE email = '{email}' AND status IS NULL "
                 f"AND prod_id = {id}")
        db_result = list(db_conn.execute(query))

        if len(db_result) > 0:
            query = ("DELETE FROM orderdetail "
                     f"WHERE orderid = {db_result[0][0]} AND prod_id = {id}")
            db_conn.execute(query)

        db_conn.close()
        return None
    except:
        _exceptionHandler(db_conn)

        return None


def db_getTitle(id):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        query = ("SELECT movietitle || ' (' || description || ')', movieid "
                 "FROM imdb_movies "
                 "NATURAL JOIN products "
                 f"WHERE prod_id = {id}")
        title = list(db_conn.execute(query))[0]

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

        query = ("SELECT DISTINCT email "
                 "FROM customers "
                 f"WHERE email = '{email}'")
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

        query = ("INSERT INTO customers(username, password, email, "
                 "creditcard, address1, balance, loyalty) "
                 f"VALUES ('{user_data['name']}', '{user_data['password']}', "
                 f"'{user_data['email']}', '{user_data['tarjeta']}', "
                 f"'{user_data['direccion']}', {user_data['saldo']}, "
                 f"{user_data['puntos']})")
        db_conn.execute(query)

        db_conn.close()
        return True
    except:
        _exceptionHandler(db_conn)

        return False

def db_loadUserData(email):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()
        user_data = {}

        query = ("SELECT username, password, balance, loyalty "
                 "FROM customers "
                 f"WHERE email = '{email}'")
        db_result = list(db_conn.execute(query))

        user_data["name"] = db_result[0][0]
        user_data["password"] = db_result[0][1]
        user_data["saldo"] = db_result[0][2]
        user_data["puntos"] = db_result[0][3]

        db_conn.close()
        return user_data
    except:
        _exceptionHandler(db_conn)

        return None

def db_createCart(email):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        query = ("SELECT orderid "
                 "FROM customers "
                 "NATURAL JOIN orders "
                 f"WHERE email = '{email}' AND status IS NULL")
        db_result = list(db_conn.execute(query))

        if len(db_result) > 0:
            db_conn.close()
            return True

        query = f"SELECT customerid FROM customers WHERE email = '{email}'"
        db_result = list(db_conn.execute(query))
        id = db_result[0][0]

        command = ("INSERT INTO orders(customerid, status, orderdate, tax) "
                   f"VALUES ({id}, NULL, CURRENT_DATE, 10)")
        db_conn.execute(command)

        db_conn.close()
        return True
    except:
        _exceptionHandler(db_conn)

        return False

def db_loadCart(email, cart):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        query = ("SELECT orderid "
                 "FROM customers "
                 "NATURAL JOIN orders "
                 f"WHERE email = '{email}' AND status IS NULL")
        db_result = list(db_conn.execute(query))

        if len(db_result) > 0:
            query = f"DELETE FROM orders WHERE orderid = {db_result[0][0]}"
            db_conn.execute(query)

        query = f"SELECT customerid FROM customers WHERE email = '{email}'"
        db_result = list(db_conn.execute(query))
        customerid = db_result[0][0]

        command = ("INSERT INTO orders(customerid, status, orderdate, tax) "
                   f"VALUES ({customerid}, NULL, CURRENT_DATE, 10)")
        db_conn.execute(command)

        # Creacion de los orderdetails
        query = ("SELECT orderid "
                 "FROM orders "
                 f"WHERE customerid = {customerid} AND status is NULL")
        db_result = list(db_conn.execute(query))
        orderid = db_result[0][0]

        for item in cart:
            query = ("INSERT INTO orderdetail(orderid, prod_id, quantity) "
                     f"VALUES ({orderid}, {item}, {cart[item]})")
            db_conn.execute(query)

        db_conn.close()
        return True
    except:
        _exceptionHandler(db_conn)

        return False

def db_getCart(email):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        query = ("SELECT orderdetail.prod_id, quantity, "
                 "movietitle || ' (' || description || ')', movieid, quantity > stock "
                 "FROM customers "
                 "NATURAL JOIN orders "
                 "NATURAL JOIN orderdetail "
                 "INNER JOIN products "
                 "ON(orderdetail.prod_id = products.prod_id) "
                 "NATURAL JOIN imdb_movies "
                 "INNER JOIN inventory "
                 "ON(inventory.prod_id = products.prod_id) "
                 f"WHERE email = '{email}' AND status is NULL")
        db_result = list(db_conn.execute(query))

        db_conn.close()
        return db_result
    except:
        _exceptionHandler(db_conn)

        return []


def db_cartCheck(email):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        query = ("SELECT orderid, COUNT(*)"
                 "FROM customers "
                 "NATURAL JOIN orders "
                 "NATURAL JOIN orderdetail "
                 f"WHERE email = '{email}' AND status IS NULL "
                 "GROUP BY orderid")
        db_result = list(db_conn.execute(query))

        if len(db_result) == 0 or db_result[0][1] == 0:
            db_conn.close()
            return False

        db_conn.close()
        return True
    except:
        _exceptionHandler(db_conn)

        return False


def db_getCartPrice(email):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Actualizacion de precio en orderdetail
        query = ("UPDATE orderdetail "
                 "SET price = products.price "
                 "FROM customers NATURAL JOIN orders, products "
                 f"WHERE email = '{email}' AND status IS NULL "
                 "AND orderdetail.orderid = orders.orderid AND products.prod_id = orderdetail.prod_id")
        db_conn.execute(query)

        # Calculo total carrito
        query = ("SELECT totalamount "
                 "FROM customers "
                 "NATURAL JOIN orders "
                 f"WHERE email = '{email}' AND status IS NULL ")
        db_result = list(db_conn.execute(query))

        db_conn.close()
        return db_result[0][0]
    except:
        _exceptionHandler(db_conn)

        return None


def db_saveOrder(email, points):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        if points:
            points_field = "TRUE"
        else:
            points_field = "FALSE"

        query = ("UPDATE orders "
                 f"SET status = 'Paid', "
                 f"orderdate = CURRENT_DATE, "
                 f"points = {points_field}")
        db_conn.execute(query)

        db_conn.close()
        return None
    except:
        _exceptionHandler(db_conn)

        return None


def db_getHistory(email):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        query = ("SELECT orderid, orderdate, totalamount "
                 "FROM orders "
                 "NATURAL JOIN customers "
                 f"WHERE email = '{email}' AND status IS NOT NULL "
                 "ORDER BY orderdate DESC")
        orders = db_conn.execute(query)

        db_result = []
        for row in orders:
            query = ("SELECT "
                     "movietitle || ' (' || description || ')', "
                     "quantity, orderdetail.price "
                     "FROM orderdetail "
                     "INNER JOIN products "
                     "ON(orderdetail.prod_id = products.prod_id) "
                     "NATURAL JOIN imdb_movies "
                     f"WHERE orderid = {row['orderid']}")
            details = list(db_conn.execute(query))
            db_result.append((row['orderdate'], row['totalamount'], details))

        db_conn.close()
        return db_result
    except:
        _exceptionHandler(db_conn)

        return []

def db_addBalance(email, amount):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        query = ("UPDATE customers "
                 f"SET balance = balance + {amount} "
                 f"WHERE email = '{email}'")
        db_conn.execute(query)
        db_conn.close()
    except:
        _exceptionHandler(db_conn)

def db_getUserFinancialInfo(email):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        query = ("SELECT balance, loyalty, creditcard "
                 "FROM customers "
                 f"WHERE email = '{email}'")
        db_result = list(db_conn.execute(query))[0]

        db_conn.close()
        return db_result
    except:
        _exceptionHandler(db_conn)
        return []


def db_getTopActors(genre='Action', n_top=10):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        query = ("SELECT movieid, actor, num, debut, film, director "
                 f"FROM getTopActors('{genre}') "
                 "INNER JOIN imdb_movies ON (movietitle = film) "
                 "ORDER BY num DESC, film DESC "
                 f"LIMIT {n_top}")
        db_result = db_conn.execute(query)

        db_conn.close()
        return db_result
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
