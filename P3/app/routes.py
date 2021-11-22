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
        dbr = database.delCity(city, bFallo, bSQL=='1', int(duerme), bCommit)
        return render_template('borraCiudad.html', dbr=dbr)
    else:
        return render_template('borraCiudad.html')

    
@app.route('/topUK', methods=['POST','GET'])
def topUK():
    # TODO: consultas a MongoDB ...
    movies=[[],[],[]]
    topUK = getMongoCollection(mongo_client)

    # Consulta para tabla Sci-fi
    for film in topUK.find({"year": {"$in": [y for y in range(1994, 1999)]}, "genres": "Sci-Fi"}):
        movies[0].append(film)

    # Consulta para tabla dramas
    for film in topUK.find({"year": 1998, "genres": "Drama", "title": {"$regex": ", The"}}):
        movies[1].append(film)

    # Consulta para peliculas de JR y AB
    for film in topUK.find({"actors": {"$all": ["Roberts, Julia", "Baldwin, Alec"]}}):
        movies[2].append(film)


    return render_template('topUK.html', movies=movies)