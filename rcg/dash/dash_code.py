from dash import html
from dash.dcc import Graph
from plotly.graph_objects import Figure, Bar
from ..web.chart_class import Chart
from ..config.config import COLORS

class BarGrapher:
    """
    Splitting this out for easier code nav and consolidation of purpose.

    load_plot from Chart, bar_charter and bar_charts from GridMaker
    """
    def __init__(self, c: Chart):
        self.c = c
        return

    def load_plot(self, normalize: bool=False) -> Figure:
        """
        Creates the bar plot for both total and normalized counts.
        """
        count_df, title = self.c.count_df(normalize)

        fig = Figure(
            Bar(
                x=count_df['gender'], 
                y=count_df['count'],
                marker_color=list(COLORS.values()),
                text=count_df['count'],
                textposition='outside'
            )
        )
        
        fig.update_layout(
            title = {
                'text':title,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'bottom'
            },
            yaxis_range=[0,110] if normalize else [
                0, count_df['count'].max()*1.2],
            margin=dict(t=70, r=20, l=20, b=30),
            paper_bgcolor="white",
            plot_bgcolor="white",
            autosize=True
            )

        if normalize:
            fig.update_traces(texttemplate='%{y:.1f}%')

        return fig

    def bar_charter(self, id_, fig) -> Graph:
        class_name = 'bar-chart l' if id_=='total' else 'bar-chart r'
        return html.Div(Graph(
            id=id_, 
            figure=fig, 
            config={
                'staticPlot': True,
                'format': 'svg',
                'displayModeBar': False
                }
            ), className=class_name)

    @property
    def bar_charts(self) -> list:
        return [
            html.Div(
                [
                    self.bar_charter('total', self.load_plot(False)), 
                    self.bar_charter('pct', self.load_plot(True))],
                className="bar-chart-container"
            )
            ]