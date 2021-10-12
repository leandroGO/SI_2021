from app import app
from flask import (render_template, request, url_for, redirect, session,
                   make_response)
import json
import os
import hashlib
import pickle
from random import randrange

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    update_cookie = False
    if "usuario" in session:
        return redirect('/')

    if request.method == 'GET': # El cliente solicita el formulario
        session["url_previo"] = request.referrer
        last_username = request.cookies.get("last_username")
        if last_username:
            username = last_username
        else:
            username = None
        return render_template("login.html", username=username)

    # if request.method == 'POST'
    if "user" in request.form:
        username = request.form["user"]
        user_path = os.path.join(app.root_path, "../usuarios/" + username)
        if not os.path.exists(user_path):
            return render_template("login.html",
                                   error=f"El usuario {username} no existe")

        user_data_path = os.path.join(user_path, "datos.dat")
        with open(user_data_path, 'rb') as f:
            user_data = pickle.load(f)

        if "password" in request.form:
            submitted_password = request.form["password"]
            salt = user_data["salt"]
            h = hashlib.blake2b(salt + submitted_password.encode('utf-8'))
            if h.hexdigest() != user_data["password_salted_hash"]:
                return render_template("login.html", username=username,
                                       error=f"Contraseña incorrecta")

            session["usuario"] = user_data["name"]
            update_cookie = True

    if "url_origen" in session: # url a la que volver a toda costa
        url_destino = session["url_origen"]
    elif "url_previo" in session:
        url_destino = session["url_previo"]
    else:
        url_destino = request.referrer

    response = make_response(redirect(url_destino))

    if update_cookie:
        response.set_cookie("last_username", request.form["user"])

    return response


@app.route('/register', methods=['GET', 'POST'])
def register():
    if "usuario" in session:
        return redirect('/')

    if request.method == 'GET':
        return render_template("registro.html")

    # if request.method == 'POST'
    if "reg_user" in request.form:
        username = request.form["reg_user"]
        user_path = os.path.join(app.root_path, "../usuarios/" + username)
        if os.path.exists(user_path):
            return render_template("registro.html", form=request.form,
                                   error=f"El usuario {username} ya existe")

        try:
            # Todos los permisos para el usuario, solo lectura para el resto
            old_umask = os.umask(0o033)
            os.makedirs(user_path)
        finally:
            os.umask(old_umask)

        # Almacena los datos
        user_data = {}
        user_data["name"] = request.form["reg_user"]
        user_data["email"] = request.form["reg_email"]
        user_data["tarjeta"] = request.form["reg_tarjeta"]
        user_data["direccion"] = request.form["reg_direccion"]
        user_data["saldo"] = randrange(101)

        salt = os.urandom(16)
        user_data["salt"] = salt
        h = hashlib.blake2b(salt + request.form["reg_password"].encode('utf-8'))
        user_data["password_salted_hash"] = h.hexdigest()

        user_data_path = os.path.join(user_path, "datos.dat")
        with open(user_data_path, 'wb') as f:
            pickle.dump(user_data, f)

    return redirect('/') # TODO: hacer que vaya a la página previa (referral)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop("usuario", None)
    return redirect('/')


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


@app.route('/ajax')
def user_count():
    nusers = randrange(1000)
    return "{} usuarios conectados".format(nusers)
