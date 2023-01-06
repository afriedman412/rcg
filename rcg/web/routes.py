from flask import Blueprint, render_template
from ..code.helpers import load_chart
from .chart_class import Chart

web_routes = Blueprint("web_routes", __name__)

@web_routes.route("/")
@web_routes.route("/<chart_date>")
@web_routes.route("/web/<chart_date>")
def home_with_date(chart_date: str=None):
    full_chart, chart_date = load_chart(chart_date)
    chart = Chart(full_chart, chart_date)
    return render_template("home.html", chart=chart)