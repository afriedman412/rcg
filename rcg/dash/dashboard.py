from dash import Dash, html
from .dash_code import BarGrapher

def init_dashboard(server, db):
    """Create a Plotly Dash dashboard."""
    dash_app = Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[
            '/static/styles/stylesheet.css',
        ]
    )
    bg = BarGrapher()
    # Create Dash Layout
    dash_app.layout = html.Div(
        className="wrapper",
         children = bg.bar_charts())

    return dash_app.server