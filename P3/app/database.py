# -*- coding: utf-8 -*-

import os
import sys, traceback, time

from sqlalchemy import (create_engine, delete, Table, Column, Integer,
                        String, MetaData, ForeignKey, text, desc)
from pymongo import MongoClient

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False,
    execution_options={"autocommit":False})
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
    mongoDB_client.close();

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
    # - suspender la ejecución 'duerme' segundos en el punto adecuado para forzar deadlock
    # - ir guardando trazas mediante dbr.append()

    try:
        # TODO: ejecutar consultas
        conn = dbConnect()

        if bSQL:
            del1 = ("DELETE FROM orderdetail "
                    "USING orders NATURAL JOIN customers "
                    "WHERE orderdetail.orderid = orders.orderid "
                    f"AND city = '{city}'")
            del2 = ("DELETE FROM orders "
                    "USING customers "
                    "WHERE orders.customerid = customers.customerid "
                    f"AND city = '{city}'")
            del3 = f"DELETE FROM customers WHERE city = '{city}'"
        else:
            # Usando SQLAlchemy
            del1 = (delete(db_orderdetail)
                .where(db_customers.c.city == city)
                .where(db_orderdetail.c.orderid == db_orders.c.orderid)
                .where(db_customers.c.customerid == db_orders.c.customerid))
            del2 = (delete(db_orders)
                .where(db_customers.c.city == city)
                .where(db_customers.c.customerid == db_orders.c.customerid))
            del3 = delete(db_customers).where(db_customers.c.city == city)

            transaction = conn.begin()
            conn.execute(del1)
            if bCommit:
                transaction.commit()
                dbr.append("Commit intermedio")
                transaction = conn.begin()

            if bFallo:
                conn.execute(del3)
                conn.execute(del2)
            else:
                conn.execute(del2)
                conn.execute(del3)
            transaction.commit()
    except Exception as e:
        transaction.rollback()
        conn.close()
        dbr.append(e)

    else:
        conn.close()
        dbr.append("Bien")

    return dbr

