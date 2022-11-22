from dash import Dash, html
from .dash_code import BarGrapher
from ..code.helpers import load_chart

def init_dashboard(server, db_):
    """Create a Plotly Dash dashboard."""
    dash_app = Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[
            '/static/styles/stylesheet.css',
        ]
    )
    
    full_chart, chart_date = load_chart(db_)
    bg = BarGrapher(full_chart, chart_date)
    # Create Dash Layout
    dash_app.layout = html.Div(
        className="wrapper",
         children = bg.bar_charts)

    return dash_app.server