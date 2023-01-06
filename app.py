"""Application entry point."""
from rcg import app

# Import parts of our core Flask app
from rcg.db.routes import db_routes
from rcg.web.routes import web_routes

app.register_blueprint(db_routes)
app.register_blueprint(web_routes)


if __name__ == "__main__":
    app.run()