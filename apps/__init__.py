# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module

from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

DB_NAME = 'db.sqlite3'
DEVELOPER_MODE = True

db = SQLAlchemy()
login_manager = LoginManager()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    for module_name in ('authentication', 'home'):
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):

    @app.before_first_request
    def initialize_database():
        try:
            db.create_all()
        except Exception as e:

            print('> Error: DBMS Exception: ' + str(e) )

            # fallback to SQLite
            basedir = os.path.abspath(os.path.dirname(__file__))
            app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, DB_NAME)

            print('> Fallback to SQLite ')
            db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()



def create_app(config):
    
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    
    return app


class _dict(dict):
    """dict like object that exposes keys as attributes"""

    __slots__ = ()
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    __setstate__ = dict.update

    def __getstate__(self):
        return self

    def update(self, *args, **kwargs):
        """update and return self -- the missing dict feature in python"""

        super().update(*args, **kwargs)
        return self

    def copy(self):
        return _dict(self)
    


def list2_dict(list, keys):
    data = []
    for l in list:
        data.append(_dict(zip(keys, l)))
    return data



    


