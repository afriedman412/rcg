from dash import Dash, html
from dash.dcc import Location
from dash.dependencies import Input, Output
import os
from .dash_code import bar_grapher_generator
from ..code.helpers import load_chart

def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    dash_app = Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[
            '/static/styles/stylesheet.css',
        ]
    )
    bg = bar_grapher_generator()
    dash_app.layout = html.Div([
        Location(id='url', refresh=False), 
        html.Div(
            bg.bar_charts,
            className="holder-holder",
            id="holder-holder")
        ])
    init_callbacks(dash_app)

    return dash_app.server

def init_callbacks(dash_app):
    @dash_app.callback(
    Output("holder-holder", 'children'),
    Input("url", "pathname")
    )
    def reload_graphs(pathname):
        date_ = pathname.split("/")[-1]
        bg_ = bar_grapher_generator(date_)
        return bg_.bar_charts






