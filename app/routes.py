from app import app
from flask import render_template, request, url_for, redirect, session
import json
import os

@app.route('/', methods=["GET", "POST"])
def home():
    lista = []
    path = os.path.join(app.root_path, "static/peliculas.json")
    with open(path) as json_data:
        peliculas = json.load(json_data)["peliculas"]

    if request.method == "POST":
        data = request.form

        if data["genero"] == "todas":
            for pelicula in peliculas.keys():
                if data["busqueda"].lower() in peliculas[pelicula]["titulo"].lower():
                    lista.append((peliculas[pelicula]["titulo"], pelicula))
        else:
           for pelicula in peliculas.keys():
                if data["busqueda"] in peliculas[pelicula]["titulo"] and peliculas[pelicula]["categoria"].lower() == data["genero"]:
                    lista.append((peliculas[pelicula]["titulo"], pelicula))

    else:
        for pelicula in peliculas.keys():
            lista.append((peliculas[pelicula]["titulo"], pelicula))

    return render_template("lista_peliculas.html", lista=lista)


@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET': # El cliente solicita el formulario
        return render_template("registro.html")

    # if request.method == 'POST'
    if "reg_user" in request.form:
        username = request.form["reg_user"]
        app.logger.info(username)
        user_path = os.path.join(app.root_path, "usuarios/" + username)
        if os.path.exists(user_path):
            return render_template("registro.html")

        try:
            # Todos los permisos para el usuario, solo lectura para el resto
            old_umask = os.umask(0o033)
            os.makedirs(user_path)
        finally:
            os.umask(old_umask)

    return redirect('/') # TODO: hacer que vaya a la página previa (referral)


@app.route('/pelicula/<int:id>')
def detalle(id):
    path = os.path.join(app.root_path, "static/peliculas.json")
    with open(path) as json_data:
        peliculas = json.load(json_data)["peliculas"]

    pelicula = peliculas[str(id)]

    reparto = ""
    for actor in pelicula["actores"]:
        reparto += ", {}".format(actor)

    return render_template("detalle.html", titulo=pelicula["titulo"], anno=pelicula["anno"],
            director=pelicula["director"], reparto=reparto[2:], categoria=pelicula["categoria"],
            precio=pelicula["precio"], img=url_for('static', filename=pelicula["poster"]))
