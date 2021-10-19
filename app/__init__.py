#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask
import os
import sys

app = Flask(__name__)

# ejemplo de sesion Flask: http://flask.pocoo.org/docs/1.0/quickstart/#sessions
app.secret_key = b'\xf4\xbd\xf0\xe1\xcc\xed\xd6\xc1\x12!\xeb\xc4\xe9y\xd7\xd6'
try:
    from flask_session import Session
    this_dir = os.path.dirname(os.path.abspath(__file__))
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = this_dir + '/thesessions'
    SESSION_COOKIE_NAME = 'flasksessionid'
    app.config.from_object(__name__)
    # app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
    Session(app)
    sys.stderr.write("Usando sesiones de Flask-Session en fichero del"
                     "servidor\n")
except ImportError:
    sys.stderr.write("Flask-Session no disponible, usando sesiones de Flask"
                     "en cookie")

from app import routes
