from app import app, database
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
    generos = database.db_genres()

    if request.method == "POST":
        data = request.form

        titulo_buscado = data["busqueda"]
        if data["genero"] == "todas":
            lista = database.db_search(titulo_buscado, None)
        else:
            lista = database.db_search(titulo_buscado, data["genero"])
    else:
        lista = database.db_movieList()

    return render_template("lista_peliculas.html", generos=generos,
                           lista=lista)


@app.route('/login', methods=['GET', 'POST'])
def login():
    update_cookie = False
    if "usuario" in session:
        return redirect(url_for('home'))
    path = os.path.join(app.root_path, "static/peliculas.json")
    with open(path) as json_data:
        generos = json.load(json_data)["generos"]

    if request.method == 'GET':  # El cliente solicita el formulario
        session["url_previo"] = request.referrer
        last_username = request.cookies.get("last_username")
        if last_username:
            username = last_username
        else:
            username = None

        return render_template("login.html", generos=generos,
                               username=username)

    # if request.method == 'POST'
    if "user" in request.form:
        username = request.form["user"]
        user_path = os.path.join(app.root_path, "../usuarios/" + username)
        if not os.path.exists(user_path):
            return render_template("login.html", generos=generos,
                                   error=f"El usuario {username} no existe")

        user_data = cargar_datos_usuario(username)

        if "password" in request.form:
            submitted_password = request.form["password"]
            salt = user_data["salt"]
            h = hashlib.blake2b(salt + submitted_password.encode('utf-8'))
            if h.hexdigest() != user_data["password_salted_hash"]:
                return render_template("login.html", generos=generos,
                                       username=username,
                                       error="Contraseña incorrecta")

            session["usuario"] = user_data["name"]
            update_cookie = True

    if "url_previo" in session and session["url_previo"] is not None:
        url_destino = session["url_previo"]
    elif request.referrer is not None:
        url_destino = request.referrer
    else:
        url_destino = '/'

    response = make_response(redirect(url_destino))

    if update_cookie:
        response.set_cookie("last_username", request.form["user"])

    return response


@app.route('/register', methods=['GET', 'POST'])
def register():
    if "usuario" in session:
        return redirect(url_for('home'))

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
        h = hashlib.blake2b(salt +
                            request.form["reg_password"].encode('utf-8'))
        user_data["password_salted_hash"] = h.hexdigest()

        guardar_datos_usuario(username, user_data)

    return redirect(url_for('login'))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop("usuario", None)
    session.pop("carrito", None)
    return redirect(url_for('home'))


@app.route('/pelicula/<string:id>')
def pelicula(id):
    generos = database.db_genres()
    pelicula, reparto, categorias, directores, precios = database.movieInfo(id)

    return render_template("detalle.html", pelicula=pelicula[0],
                            reparto=reparto,
                            categorias=categorias,
                            directores=directores,
                            precios=precios,
                            generos=generos)


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


@app.route('/add')
def add():
    path = os.path.join(app.root_path, "static/peliculas.json")
    with open(path) as json_data:
        data = json.load(json_data)
        peliculas = data["peliculas"]
        generos = data["generos"]

    if id not in peliculas:
        return render_template("error.html", generos=generos)

    # No hay carrito
    if "carrito" not in session:
        carrito = {id: 1}
        session["carrito"] = carrito

    # Carrito ya creado sin la pelicula
    elif id not in session["carrito"]:
        session["carrito"][id] = 1

    # Carrito contiene pelicula, se incrementa cantidad
    else:
        session["carrito"][id] += 1

    session.modified = True
    return redirect(url_for('carrito'))


@app.route('/sub/<string:id>')
def sub(id):
    if ("carrito" in session
            and id in session["carrito"]
            and session["carrito"][id] > 1):
        session["carrito"][id] -= 1
        session.modified = True

    return redirect(url_for('carrito'))


@app.route('/delete/<string:id>')
def delete(id):
    if "carrito" in session and id in session["carrito"]:
        session["carrito"].pop(id)
        session.modified = True

    return redirect(url_for('carrito'))


@app.route('/buy')
def buy():
    path = os.path.join(app.root_path, "static/peliculas.json")
    with open(path) as json_data:
        data = json.load(json_data)
        peliculas = data["peliculas"]
        generos = data["generos"]

    if "usuario" not in session:
        return redirect(url_for('login'))

    if "carrito" not in session or len(session["carrito"]) == 0:
        return render_template("error.html", generos=generos)

    # Usuario con sesion iniciada
    username = session["usuario"]
    user_data = cargar_datos_usuario(username)
    saldo = user_data["saldo"]
    puntos = user_data["puntos"]

    count = 0
    for pelicula in session["carrito"]:
        count += peliculas[pelicula]["precio"] * session["carrito"][pelicula]

    session["subtotal"] = count
    return render_template("pago.html", generos=generos, precio=count,
                           saldo=saldo, puntos=puntos)


@app.route('/saldo')
def saldo():
    path = os.path.join(app.root_path, "static/peliculas.json")
    with open(path) as json_data:
        generos = json.load(json_data)["generos"]

    if "usuario" not in session:
        return redirect(url_for('login'))

    if "carrito" not in session or "subtotal" not in session:
        return render_template("error.html", generos=generos)

    username = session["usuario"]
    user_data = cargar_datos_usuario(username)

    # Actualizacion saldo
    if session["subtotal"] > user_data["saldo"]:
        return redirect(url_for('home'))

    user_data["saldo"] -= session["subtotal"]

    # Actualizacion puntos
    user_data["puntos"] += int(session["subtotal"]*5)

    guardar_datos_usuario(username, user_data)
    return guardar_compra()


@app.route('/puntos')
def puntos():
    path = os.path.join(app.root_path, "static/peliculas.json")
    with open(path) as json_data:
        generos = json.load(json_data)["generos"]

    if "usuario" not in session:
        return redirect(url_for('login'))

    if "carrito" not in session or "subtotal" not in session:
        return render_template("error.html", generos=generos)

    username = session["usuario"]
    user_data = cargar_datos_usuario(username)

    # Actualizacion saldo
    if session["subtotal"]*100 > user_data["puntos"]:
        return redirect(url_for('home'))

    user_data["puntos"] -= int(session["subtotal"]*100)

    # Actualizacion puntos
    user_data["puntos"] += int(session["subtotal"]*5)

    guardar_datos_usuario(username, user_data)
    return guardar_compra()


@app.route('/historial', methods=['GET', 'POST'])
def historial():
    if "usuario" not in session:
        return redirect(url_for('login'))

    username = session["usuario"]
    path = os.path.join(app.root_path, "../usuarios/", username,
                        "historial.json")

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
    puntos = int(user_data["puntos"])   # Por si acaso, debería ser entero
    return render_template("historial.html", generos=generos,
                           historial=historial, saldo=saldo, puntos=puntos,
                           tarjeta=tarjeta_ofuscada)


@app.route('/ajax')
def ajax():
    nusers = randrange(1000)
    return "{} usuarios conectados".format(nusers)


# Funciones auxiliares
def guardar_compra():
    path = os.path.join(app.root_path, "static/peliculas.json")
    with open(path, "r") as f:
        peliculas = json.load(f)["peliculas"]

    username = session["usuario"]

    path = os.path.join(app.root_path, "../usuarios/", username,
                        "historial.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            historial = json.load(f)
    else:
        historial = dict()

    # Actualizacion historial
    subtotal = session["subtotal"]
    compra = []
    for item in session["carrito"]:
        compra.append((peliculas[item]["titulo"], peliculas[item]["precio"],
                       session["carrito"][item]))
    historial[datetime.now().strftime("%Y-%m-%d (%H:%M:%S)")] = (subtotal,
                                                                 compra)

    with open(path, "w") as f:
        json.dump(historial, f)

    session.pop("carrito")

    return redirect(url_for('historial'))


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
