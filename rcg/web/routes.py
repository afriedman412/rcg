from flask import Blueprint, render_template
from .chart_class import Chart

web_routes = Blueprint("web_routes", __name__)

@web_routes.route("/")
def home():
    chart = Chart()
    return render_template("home.html", chart=chart)