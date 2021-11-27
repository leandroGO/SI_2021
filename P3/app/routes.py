#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from app.database import *
from flask import render_template, request, url_for
import os
import sys
import time

@app.route('/', methods=['POST','GET'])
@app.route('/index', methods=['POST','GET'])
def index():
    return render_template('index.html')


@app.route('/borraCiudad', methods=['POST','GET'])
def borraCiudad():
    if 'city' in request.form:
        city    = request.form["city"]
        bSQL    = request.form["txnSQL"]
        bCommit = "bCommit" in request.form
        bFallo  = "bFallo"  in request.form
        duerme  = request.form["duerme"]
        dbr = delCity(city, bFallo, bSQL=='1', int(duerme), bCommit)
        return render_template('borraCiudad.html', dbr=dbr)
    else:
        return render_template('borraCiudad.html')


@app.route('/topUK', methods=['POST','GET'])
def topUK():
    movies=[[],[],[]]
    topUK = getMongoCollection(mongo_client)

    # Consulta para tabla Sci-fi
    movies[0] = list(topUK.find({"year": {'$gte': 1994, '$lte': 1998}, "genres": "Sci-Fi"}))

    # Consulta para tabla dramas
    movies[1] = topUK.find({"year": 1998, "genres": "Drama", "title": {"$regex": ".*, The"}})

    # Consulta para peliculas de JR y AB
    movies[2] = topUK.find({"actors": {"$all": ["Roberts, Julia", "Baldwin, Alec"]}})

    return render_template('topUK.html', movies=movies)
