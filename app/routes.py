from app import app
from flask import (render_template, request, url_for, redirect, session,
                   make_response)
import json
import os
import hashlib
import pickle
from random import randrange
from datetime import datetime


@app.route('/', methods=["GET", "POST"])
def home():
    lista = []
    path = os.path.join(app.root_path, "static/peliculas.json")
    with open(path) as json_data:
        data = json.load(json_data)
        peliculas = data["peliculas"]
        generos = data["generos"]

    if request.method == "POST":
        data = request.form

        if data["genero"] == "todas":
            for pelicula in peliculas:
                if data["busqueda"].lower() in peliculas[pelicula]["titulo"].lower():
                    lista.append((peliculas[pelicula]["titulo"], pelicula))
        else:
           for pelicula in peliculas:
                if data["busqueda"].lower() in peliculas[pelicula]["titulo"].lower() and peliculas[pelicula]["categoria"] == data["genero"]:
                    lista.append((peliculas[pelicula]["titulo"], pelicula))

    else:
        for pelicula in peliculas.keys():
            lista.append((peliculas[pelicula]["titulo"], pelicula))

    return render_template("lista_peliculas.html", generos=generos, lista=lista)


@app.route('/login', methods=['GET', 'POST'])
def login():
    update_cookie = False
    if "usuario" in session:
        return redirect('/')
    path = os.path.join(app.root_path, "static/peliculas.json")
    with open(path) as json_data:
        generos = json.load(json_data)["generos"]

    if request.method == 'GET': # El cliente solicita el formulario
        session["url_previo"] = request.referrer
        last_username = request.cookies.get("last_username")
        if last_username:
            username = last_username
        else:
            username = None

        return render_template("login.html", generos=generos, username=username)

    # if request.method == 'POST'
    if "user" in request.form:
        username = request.form["user"]
        user_path = os.path.join(app.root_path, "../usuarios/" + username)
        if not os.path.exists(user_path):
            return render_template("login.html", generos=generos,
                                   error=f"El usuario {username} no existe")

        user_data_path = os.path.join(user_path, "datos.dat")
        with open(user_data_path, 'rb') as f:
            user_data = pickle.load(f)

        if "password" in request.form:
            submitted_password = request.form["password"]
            salt = user_data["salt"]
            h = hashlib.blake2b(salt + submitted_password.encode('utf-8'))
            if h.hexdigest() != user_data["password_salted_hash"]:
                return render_template("login.html", generos=generos, username=username,
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
        path = os.path.join(app.root_path, "static/peliculas.json")
        with open(path) as json_data:
            generos = json.load(json_data)["generos"]
        return render_template("registro.html", generos=generos)

    # if request.method == 'POST'
    if "reg_user" in request.form:
        username = request.form["reg_user"]
        user_path = os.path.join(app.root_path, "../usuarios/", username)
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
        user_data["puntos"] = 0

        salt = os.urandom(16)
        user_data["salt"] = salt
        h = hashlib.blake2b(salt + request.form["reg_password"].encode('utf-8'))
        user_data["password_salted_hash"] = h.hexdigest()

        guardar_datos_usuario(username, user_data)

    return redirect('/') # TODO: hacer que vaya a la página previa (referral)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop("usuario", None)
    session.pop("carrito", None)
    return redirect('/')


@app.route('/pelicula/<int:id>')
def detalle(id):
    path = os.path.join(app.root_path, "static/peliculas.json")
    with open(path) as json_data:
        data = json.load(json_data)
        peliculas = data["peliculas"]
        generos = data["generos"]

    pelicula = peliculas[str(id)]

    reparto = ""
    for actor in pelicula["actores"]:
        reparto += ", {}".format(actor)

    return render_template("detalle.html", titulo=pelicula["titulo"], anno=pelicula["anno"],
            director=pelicula["director"], reparto=reparto[2:], categoria=pelicula["categoria"],
            precio=pelicula["precio"], img=url_for('static', filename=pelicula["poster"]),
            id=str(id), generos=generos)


@app.route('/carrito')
def carrito():
    context = []
    if "carrito" in session:
        lista = session["carrito"]
    else:
        lista = dict()

    path = os.path.join(app.root_path, "static/peliculas.json")
    with open(path) as json_data:
        data = json.load(json_data)
        peliculas = data["peliculas"]
        generos = data["generos"]

    for item in lista.keys():
        context.append((item, lista[item], peliculas[item]["titulo"]))
    print(context)
    return render_template("carrito.html", generos=generos, lista=context)

@app.route('/add/<int:id>')
def add(id):
    # No hay carrito
    if "carrito" not in session:
        carrito = {str(id): 1}
        session["carrito"] = carrito

    # Carrito ya creado sin la pelicula
    elif str(id) not in session["carrito"]:
        session["carrito"][str(id)] = 1

    # Carrito contiene pelicula, se incrementa cantidad
    else:
        session["carrito"][str(id)] += 1

    session.modified = True
    return redirect('/carrito')

@app.route('/sub/<int:id>')
def sub(id):
    if "carrito" in session and str(id) in session["carrito"] and session["carrito"][str(id)] > 1:
        session["carrito"][str(id)] -= 1
        session.modified = True

    return redirect('/carrito')

@app.route('/delete/<int:id>')
def delete(id):
    if "carrito" in session and str(id) in session["carrito"]:
        session["carrito"].pop(str(id))
        session.modified = True

    return redirect('/carrito')

@app.route('/buy')
def buy():
    if "usuario" not in session:
        return redirect("/login")

    if "carrito" not in session:
        return redirect("/")

    # Usuario con sesion iniciada
    username = session["usuario"]
    user_data = cargar_datos_usuario(username)
    saldo = user_data["saldo"]
    puntos = user_data["puntos"]

    path = os.path.join(app.root_path, "static/peliculas.json")
    with open(path) as json_data:
        data = json.load(json_data)
        peliculas = data["peliculas"]
        generos = data["generos"]

    count = 0
    for pelicula in session["carrito"]:
        count += peliculas[pelicula]["precio"] * session["carrito"][pelicula]

    session["subtotal"] = count
    return render_template("pago.html", generos=generos, precio=count, saldo=saldo, puntos=puntos)

@app.route('/saldo')
def saldo():
    if "usuario" not in session:
        return redirect("/login")

    if "carrito" not in session or "subtotal" not in session:
        return redirect("/")

    username = session["usuario"]
    user_data = cargar_datos_usuario(username)

    # Actualizacion saldo
    if session["subtotal"] > user_data["saldo"]:
        return redirect("/")

    user_data["saldo"] -= session["subtotal"]

    # Actualizacion puntos
    user_data["puntos"] += session["subtotal"]*5

    guardar_datos_usuario(username, user_data)
    return guardar_compra()

@app.route('/puntos')
def puntos():
    if "usuario" not in session:
        return redirect("/login")

    if "carrito" not in session or "subtotal" not in session:
        return redirect("/")

    username = session["usuario"]
    user_data = cargar_datos_usuario(username)

    # Actualizacion saldo
    if session["subtotal"]*100 > user_data["puntos"]:
        return redirect("/")

    user_data["puntos"] -= session["subtotal"]*100

    # Actualizacion puntos
    user_data["puntos"] += session["subtotal"]*5

    with open(path, "wb") as f:
        pickle.dump(user_data, f)

    return guardar_compra()

@app.route('/historial', methods=['GET', 'POST'])
def historial():
    if "usuario" not in session:
        return redirect("/login")

    username = session["usuario"]
    path = os.path.join(app.root_path, "../usuarios/", username, "historial.json")

    if os.path.exists(path):
        with open(path, "r") as f:
            historial = json.load(f)
    else:
        historial = dict()

    path = os.path.join(app.root_path, "static/peliculas.json")
    with open(path) as json_data:
        generos = json.load(json_data)["generos"]

    user_data = cargar_datos_usuario(username)
    if request.method == 'POST' and "incremento" in request.form:
        user_data["saldo"] += float(request.form["incremento"])
        guardar_datos_usuario(username, user_data)

    saldo = user_data["saldo"]
    tarjeta = user_data["tarjeta"]
    tarjeta_ofuscada = tarjeta[-4:].rjust(len(tarjeta), '*')
    return render_template("historial.html", generos=generos,
                           historial=historial, saldo=saldo,
                           tarjeta=tarjeta_ofuscada)

@app.route('/ajax')
def user_count():
    nusers = randrange(1000)
    return "{} usuarios conectados".format(nusers)


# Funciones auxiliares
def guardar_compra():
    path = os.path.join(app.root_path, "static/peliculas.json")
    with open(path, "r") as f:
        peliculas = json.load(f)["peliculas"]

    username = session["usuario"]

    path = os.path.join(app.root_path, "../usuarios/", username, "historial.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            historial = json.load(f)
    else:
        historial = dict()

    # Actualizacion historial
    subtotal = session["subtotal"]
    compra = []
    for item in session["carrito"]:
        compra.append((peliculas[item]["titulo"], peliculas[item]["precio"], session["carrito"][item]))
    historial[datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")] = (subtotal, compra)

    with open(path, "w") as f:
        json.dump(historial, f)

    session.pop("carrito")

    return redirect('/historial')

def cargar_datos_usuario(username):
    '''Carga los datos de un usuario existente (no usar en otro caso)'''
    path = os.path.join(app.root_path, "../usuarios/", username, "datos.dat")
    with open(path, "rb") as f:
        user_data = pickle.load(f)

    return user_data

def guardar_datos_usuario(username, user_data):
    '''Guarda los datos de un usuario existente (no usar en otro caso)'''
    path = os.path.join(app.root_path, "../usuarios/", username, "datos.dat")
    with open(path, "wb") as f:
        pickle.dump(user_data, f)
