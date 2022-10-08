from .code.helpers import DataHandler
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask import render_template
from dotenv import load_dotenv
import connexion
import os

def app_factory():
    load_dotenv()
    dir_ = os.path.abspath(os.path.dirname(__file__))

    connex_app = connexion.App(__name__, specification_dir=dir_)
    app = connex_app.app
    app.config.from_pyfile('config/config.py')

    return app

app_ = app_factory()
db_ = SQLAlchemy(app_)
ma_ = Marshmallow(app_)
dh_ = DataHandler(app_)