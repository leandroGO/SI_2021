from app import app
from flask import render_template, request, url_for, redirect, session
import json

@app.route('/')
def home():
    with open("app/static/peliculas.json") as json_data:
        peliculas = json.load(json_data)["peliculas"]

    lista = []
    for pelicula in peliculas.keys():
        lista.append((peliculas[pelicula]["titulo"], pelicula))
    return render_template("lista_peliculas.html", lista=lista)

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/register')
def register():
    return render_template("registro.html")

@app.route('/pelicula/<int:id>')
def detalle(id):
    with open("app/static/peliculas.json") as json_data:
        peliculas = json.load(json_data)["peliculas"]

    pelicula = peliculas[str(id)]

    return render_template("detalle.html", titulo=pelicula["titulo"], anno=pelicula["anno"], reparto=pelicula["actores"], imagen=pelicula["poster"])
