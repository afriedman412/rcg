from flask import Blueprint, render_template
from ..code.code import load_chart, update_chart
from .chart_class import Chart

web_routes = Blueprint("web_routes", __name__)

@web_routes.route("/favicon.ico")
def load_favicon():
    return

@web_routes.route("/update")
def update():
    old_chart, old_chart_date = load_chart()
    old_chart = Chart(old_chart, old_chart_date)
    print("OLD DATE:", old_chart_date)
    update_chart()
    new_chart, new_chart_date = load_chart()
    new_chart = Chart(new_chart, new_chart_date)
    print("NEW DATE:", new_chart_date)
    added_to_chart = [s for s in new_chart.chart_w_features() if s not in old_chart.chart_w_features()]
    removed_from_chart = [s for s in old_chart.chart_w_features() if s not in new_chart.chart_w_features()]
    return render_template(
        "update.html", 
        new_chart_date=new_chart_date, 
        old_chart_date=old_chart_date,
        added_to_chart=added_to_chart,
        removed_from_chart=removed_from_chart
        )

@web_routes.route("/")
@web_routes.route("/<chart_date>")
@web_routes.route("/web/<chart_date>")
def home_with_date(chart_date: str=None):
    full_chart, chart_date = load_chart(chart_date)
    chart = Chart(full_chart, chart_date)
    return render_template("home.html", chart=chart)