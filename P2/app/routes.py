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
        top_actors = None

        titulo_buscado = data["busqueda"]
        if data["genero"] == "todas":
            lista = database.db_search(titulo_buscado, None)
        else:
            lista = database.db_search(titulo_buscado, data["genero"])
    else:
        lista = database.db_movieList()
        data = request.args
        if data:
            top_actors = database.db_getTopActors(genre=data["genero"],
                                                  n_top=data["n_top"])
        else:
            top_actors = database.db_getTopActors()

    return render_template("lista_peliculas.html", generos=generos,
                           lista=lista, top_actors=top_actors)


@app.route('/login', methods=['GET', 'POST'])
def login():
    update_cookie = False
    if "usuario" in session:
        return redirect(url_for('home'))
    generos = database.db_genres()

    if request.method == 'GET':  # El cliente solicita el formulario
        session["url_previo"] = request.referrer
        last_user_email = request.cookies.get("last_user_email")
        if last_user_email:
            user_email = last_user_email
        else:
            user_email = None

        return render_template("login.html", generos=generos,
                               user_email=user_email)

    # if request.method == 'POST'
    if "email" in request.form:
        email = request.form["email"]
        if not database.db_userCheck(email):
            return render_template("login.html", generos=generos,
                                   error=f"El email {email} no está registrado")

        user_data = database.db_loadUserData(email)
        if user_data == None:
            return render_template("login.html", generos=generos,
                                    user_email=email,
                                    error=f"Error en el acceso a base de datos")

        if "password" in request.form:
            submitted_password = request.form["password"]
            if submitted_password != user_data["password"]:
                return render_template("login.html", generos=generos,
                                       user_email=email,
                                       error="Contraseña incorrecta")

            session["usuario"] = user_data["name"]
            session["email"] = email
            update_cookie = True

    # Vinculacion de carrito a la base de datos
    if "carrito" in session:
        ret = database.db_loadCart(email, session["carrito"])
        session.pop("carrito")
    else:
        ret = database.db_createCart(email)
    if ret is False:
        return render_template("error.html", generos=generos)


    if "url_previo" in session and session["url_previo"] is not None:
        url_destino = session["url_previo"]
    elif request.referrer is not None:
        url_destino = request.referrer
    else:
        url_destino = '/'

    response = make_response(redirect(url_destino))

    if update_cookie:
        response.set_cookie("last_user_email", request.form["email"])

    return response


@app.route('/register', methods=['GET', 'POST'])
def register():
    if "usuario" in session:
        return redirect(url_for('home'))

    if request.method == 'GET':
        generos = database.db_genres()
        return render_template("registro.html", generos=generos)

    # if request.method == 'POST'
    if "reg_email" in request.form:
        email = request.form["reg_email"]

        if database.db_userCheck(email):
            return render_template("registro.html", form=request.form,
                                   error=f"El email {email} ya ha sido registrado anteriormente")

        # Almacena los datos
        user_data = {}
        user_data["name"] = request.form["reg_user"]
        user_data["password"] = request.form["reg_password"]
        user_data["email"] = request.form["reg_email"]
        user_data["tarjeta"] = request.form["reg_tarjeta"]
        user_data["direccion"] = request.form["reg_direccion"]
        user_data["saldo"] = randrange(101)
        user_data["puntos"] = 0
        ret = database.db_regUser(user_data)
        if not ret:
            return render_template("registro.html", form=request.form,
                                   error=f"Error en el acceso a base de datos")

    return redirect(url_for('login'))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop("usuario", None)
    session.pop("email", None)
    return redirect(url_for('home'))


@app.route('/pelicula/<string:id>')
def pelicula(id):
    generos = database.db_genres()
    pelicula, reparto, categorias, directores, precios = database.db_movieInfo(id)

    return render_template("detalle.html", pelicula=pelicula[0],
                            reparto=reparto,
                            categorias=categorias,
                            directores=directores,
                            precios=precios,
                            generos=generos)


@app.route('/carrito')
def carrito():
    generos = database.db_genres()
    context = []

    if "usuario" not in session:
        if "carrito" in session:
            lista = session["carrito"]
            for item in lista.keys():
                title, movieid = database.db_getTitle(item)
                context.append((item, lista[item], title, movieid))
    else:
        context = database.db_getCart(session["email"])

    return render_template("carrito.html", generos=generos, lista=context)


@app.route('/add')
def add():
    generos = database.db_genres()
    id = request.args.get("product")

    if id is None or not database.db_productCheck(id):
        return render_template("error.html", generos=generos)

    # Uso de sessions en caso de que el usuario no haya iniciado sesion    
    if "email" not in session:
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

    #Uso de la base de datos para el carrito de cada usuario    
    else:
        database.db_add(session["email"], id)

    return redirect(url_for('carrito'))


@app.route('/sub/<string:id>')
def sub(id):
    if "email" not in session:
        if ("carrito" in session
                and id in session["carrito"]
                and session["carrito"][id] > 1):
            session["carrito"][id] -= 1
            session.modified = True
    else:
        database.db_sub(session["email"], id)

    return redirect(url_for('carrito'))


@app.route('/delete/<string:id>')
def delete(id):
    if "email" not in session:
        if "carrito" in session and id in session["carrito"]:
            session["carrito"].pop(id)
            session.modified = True
    else:
        database.db_delete(session["email"], id)

    return redirect(url_for('carrito'))


@app.route('/buy')
def buy():
    generos = database.db_genres()

    if "email" not in session:
        return redirect(url_for('login'))

    if not database.db_cartCheck(session["email"]):
        return render_template("error.html", generos=generos)

    # Usuario con sesion iniciada
    user_data = database.db_loadUserData(session["email"])
    saldo = user_data["saldo"]
    puntos = user_data["puntos"]

    count = database.db_getCartPrice(session["email"])

    return render_template("pago.html", generos=generos, precio=count,
                           saldo=saldo, puntos=puntos)


@app.route('/saldo')
def saldo():
    generos = database.db_genres()

    if "email" not in session:
        return redirect(url_for('login'))

    if not database.db_cartCheck(session["email"]):
        return render_template("error.html", generos=generos)

    user_data = database.db_loadUserData(session["email"])
    count = database.db_getCartPrice(session["email"])


    # Actualizacion saldo
    if count > user_data["saldo"]:
        return render_template("error.html", generos=generos)

    user_data["saldo"] -= count

    # Actualizacion puntos
    user_data["puntos"] += int(count*5)

    database.db_saveUserData(session["email"], user_data)
    database.db_saveOrder(session["email"])
    database.db_createCart(session["email"])
    return redirect(url_for('historial'))


@app.route('/puntos')
def puntos():
    generos = database.db_genres()

    if "email" not in session:
        return redirect(url_for('login'))

    if not database.db_cartCheck(session["email"]) or "subtotal" not in session:
        return render_template("error.html", generos=generos)

    user_data = database.db_loadUserData(session["email"])
    count = database.db_getCartPrice(session["email"])

    # Actualizacion saldo
    if count*100 > user_data["puntos"]:
        return render_template("error.html", generos=generos)

    user_data["puntos"] -= int(count*95)

    database.db_saveUserData(session["email"], user_data)
    database.db_saveOrder(session["email"])
    database.db_createCart(session["email"])
    return redirect(url_for('historial'))


@app.route('/historial', methods=['GET', 'POST'])
def historial():
    if "usuario" not in session:
        return redirect(url_for('login'))

    generos = database.db_genres()
    email = session["email"]

    if request.method == 'POST' and "incremento" in request.form:
        database.db_addBalance(email, request.form["incremento"])

    historial = database.db_getHistory(email)

    saldo, puntos, tarjeta = database.db_getUserFinancialInfo(email)
    tarjeta_ofuscada = tarjeta[-4:].rjust(len(tarjeta), '*')
    return render_template("historial.html", generos=generos,
                           historial=historial, saldo=saldo, puntos=puntos,
                           tarjeta=tarjeta_ofuscada)


@app.route('/ajax')
def ajax():
    nusers = randrange(1000)
    return "{} usuarios conectados".format(nusers)