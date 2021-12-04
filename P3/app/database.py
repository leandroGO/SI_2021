# -*- coding: utf-8 -*-

import os
import sys, traceback, time

from sqlalchemy import (create_engine, delete, Table, Column, Integer,
                        String, MetaData, ForeignKey, text, desc, func)
from sqlalchemy.sql import select
from pymongo import MongoClient

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1",
                          echo=False, execution_options={"autocommit": False})
db_meta = MetaData(bind=db_engine)

db_customers = Table('customers', db_meta, autoload=True,
                     autoload_with=db_engine)

db_orders = Table('orders', db_meta, autoload=True,
                  autoload_with=db_engine)

db_orderdetail = Table('orderdetail', db_meta, autoload=True,
                       autoload_with=db_engine)

# Crea la conexión con MongoDB
mongo_client = MongoClient()


def getMongoCollection(mongoDB_client):
    mongo_db = mongoDB_client.si1
    return mongo_db.topUK


def mongoDBCloseConnect(mongoDB_client):
    mongoDB_client.close()


def dbConnect():
    return db_engine.connect()


def dbCloseConnect(db_conn):
    db_conn.close()


def delCity(city, bFallo, bSQL, duerme, bCommit):

    # Array de trazas a mostrar en la página
    dbr=[]

    # TODO: Ejecutar consultas de borrado
    # - ordenar consultas según se desee provocar un error (bFallo True) o no
    # - ejecutar commit intermedio si bCommit es True
    # - usar sentencias SQL ('BEGIN', 'COMMIT', ...) si bSQL es True
    # - suspender la ejecución 'duerme' segundos en el punto adecuado para
    #   forzar deadlock
    # - ir guardando trazas mediante dbr.append()

    try:
        conn = dbConnect()
        transaction = None

        if bSQL:
            # Usando SQL
            # Definiciones
            del1 = ("DELETE FROM orderdetail "
                    "USING orders NATURAL JOIN customers "
                    "WHERE orderdetail.orderid = orders.orderid "
                    f"AND city = '{city}'; ")
            del2 = ("DELETE FROM orders "
                    "USING customers "
                    "WHERE orders.customerid = customers.customerid "
                    f"AND city = '{city}'; ")
            del3 = f"DELETE FROM customers WHERE city = '{city}'; "

            commit = "COMMIT; "
            begin = "BEGIN; "

            q1 = ("SELECT COUNT(*) "
                  "FROM customers "
                  "NATURAL JOIN orders "
                  "NATURAL JOIN orderdetail "
                  f"WHERE city = '{city}';")

            q2 = ("SELECT COUNT(*) "
                  "FROM customers NATURAL JOIN orders "
                  f"WHERE city = '{city}';")

            q3 = ("SELECT COUNT(*) "
                  "FROM customers  "
                  f"WHERE city = '{city}';")

            # Ejecucion de consultas
            conn.execute(begin)
            res1 = list(conn.execute(q1))
            res2 = list(conn.execute(q2))
            res3 = list(conn.execute(q3))

            dbr.append(f"Inicialmente: {res3[0][0]} clientes en {city}, "
                       f"{res2[0][0]} pedidos, {res1[0][0]} detalles")

            conn.execute(del1)
            res1 = list(conn.execute(q1))
            res2 = list(conn.execute(q2))
            res3 = list(conn.execute(q3))

            dbr.append(f"Tras primera eliminacion: {res3[0][0]} clientes en "
                       f"{city}, {res2[0][0]} pedidos, {res1[0][0]} detalles")

            if bCommit:
                conn.execute(commit + begin)
                dbr.append("Commit intermedio")

            if bFallo:
                aux = del3
                del3 = del2
                del2 = aux
            else:
                # Duerme
                current_time = time.strftime("%H:%M:%S", time.localtime())
                print(f"**** [{current_time}] Duerme durante {duerme} "
                      "segundos...")
                time.sleep(duerme)

            conn.execute(del2)
            res1 = list(conn.execute(q1))
            res2 = list(conn.execute(q2))
            res3 = list(conn.execute(q3))

            dbr.append(f"Tras segunda eliminacion: {res3[0][0]} clientes en "
                       f"{city}, {res2[0][0]} pedidos, {res1[0][0]} detalles")

            conn.execute(del3)
            res1 = list(conn.execute(q1))
            res2 = list(conn.execute(q2))
            res3 = list(conn.execute(q3))

            dbr.append(f"Tras tercera eliminacion: {res3[0][0]} clientes en "
                       f"{city}, {res2[0][0]} pedidos, {res1[0][0]} detalles")

        else:
            # Usando SQLAlchemy
            # Definiciones

            del1 = (delete(db_orderdetail)
                    .where(db_customers.c.city == city)
                    .where(db_orderdetail.c.orderid == db_orders.c.orderid)
                    .where(db_customers.c.customerid ==
                           db_orders.c.customerid))
            del2 = (delete(db_orders)
                    .where(db_customers.c.city == city)
                    .where(db_customers.c.customerid ==
                           db_orders.c.customerid))
            del3 = delete(db_customers).where(db_customers.c.city == city)

            q1 = (select([func.count()])
                  .select_from(db_customers.join(db_orders)
                               .join(db_orderdetail))
                  .where(db_customers.c.city == city))

            q2 = (select([func.count()])
                  .select_from(db_customers.join(db_orders))
                  .where(db_customers.c.city == city))

            q3 = (select([func.count()])
                  .select_from(db_customers)
                  .where(db_customers.c.city == city))

            transaction = conn.begin()
            res1 = list(conn.execute(q1))
            res2 = list(conn.execute(q2))
            res3 = list(conn.execute(q3))

            dbr.append(f"Inicialmente: {res3[0][0]} clientes en {city}, "
                       f"{res2[0][0]} pedidos, {res1[0][0]} detalles")

            conn.execute(del1)

            res1 = list(conn.execute(q1))
            res2 = list(conn.execute(q2))
            res3 = list(conn.execute(q3))

            dbr.append(f"Tras primera eliminacion: {res3[0][0]} clientes en "
                       f"{city}, {res2[0][0]} pedidos, {res1[0][0]} detalles")

            if bCommit:
                transaction.commit()
                dbr.append("Commit intermedio")
                transaction = conn.begin()

            if bFallo:
                aux = del3
                del3 = del2
                del2 = aux
            else:
                # Duerme
                current_time = time.strftime("%H:%M:%S", time.localtime())
                print(f"**** [{current_time}] Duerme durante {duerme} "
                      "segundos...")
                time.sleep(duerme)

            conn.execute(del2)

            res1 = list(conn.execute(q1))
            res2 = list(conn.execute(q2))
            res3 = list(conn.execute(q3))

            dbr.append(f"Tras segunda eliminacion: {res3[0][0]} clientes en "
                       f"{city}, {res2[0][0]} pedidos, {res1[0][0]} detalles")

            conn.execute(del3)

            res1 = list(conn.execute(q1))
            res2 = list(conn.execute(q2))
            res3 = list(conn.execute(q3))

            dbr.append(f"Tras tercera eliminacion: {res3[0][0]} clientes en "
                       f"{city}, {res2[0][0]} pedidos, {res1[0][0]} detalles")

    except Exception as e:
        if bSQL:
            conn.execute("ROLLBACK;")
        elif transaction:
            transaction.rollback()

        print(e)

        dbr.append(e)

        res1 = list(conn.execute(q1))
        res2 = list(conn.execute(q2))
        res3 = list(conn.execute(q3))

        dbr.append(f"Finalmente: {res3[0][0]} clientes en {city}, "
                   f"{res2[0][0]} pedidos, {res1[0][0]} detalles")

        conn.close()
    else:
        if bSQL:
            conn.execute(commit)
        else:
            transaction.commit()

        res1 = list(conn.execute(q1))
        res2 = list(conn.execute(q2))
        res3 = list(conn.execute(q3))

        dbr.append(f"Finalmente: {res3[0][0]} clientes en {city}, "
                   f"{res2[0][0]} pedidos, {res1[0][0]} detalles")

        conn.close()
        dbr.append("Transaccion realizada con exito")

    return dbr
