from dash import html
from dash.dcc import Graph
from pandas import DataFrame
from plotly.graph_objects import Figure, Bar
from ..config.config import COLORS
from ..code.helpers import get_date


class BarGrapher:
    """
    Splitting this out for easier code nav and consolidation of purpose.

    load_plot from Chart, bar_charter and bar_charts from GridMaker

    Redundant for now, only doing this to test Dash integration!
    """
    def __init__(self, full_chart: DataFrame, chart_date: str=None):
        self.full_chart = full_chart
        self.chart_date = chart_date if chart_date else get_date()
        return

    def load_plot(self, normalize: bool=False) -> Figure:
        """
        Creates the bar plot for both total and normalized counts.
        """
        
        if normalize:
            count_df = self.full_chart['gender'].value_counts(normalize=True).round(3)*100
            title = f"% of Artist Credits<br>({self.chart_date})"
            
        else:
            count_df =  self.full_chart['gender'].value_counts()
            title = f"Total Artist Credits<br>({self.chart_date})"

        count_df = count_df.rename_axis('gender').reset_index(name='count')
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