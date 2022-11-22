"""Initialize Flask app."""
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import connexion
from dotenv import load_dotenv
import os

def init_app():
    """
    Construct core Flask application with embedded Dash app.
    
    Adapted to add SQLAlchemy and Marshmallow functionality
    """
    load_dotenv()
    dir_ = os.path.abspath(os.path.dirname(__file__))

    connex_app = connexion.App(__name__, specification_dir=dir_)
    app = connex_app.app
    app.config.from_pyfile('config/config.py')

    with app.app_context():
        # Import Dash application
        from .dash.dashboard import init_dashboard
        app = init_dashboard(app)

        return app

def yield_db_ma(app):
    return SQLAlchemy(app), Marshmallow(app)

app = init_app()
db_, ma_ = yield_db_ma(app)