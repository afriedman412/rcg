import plotly.express as px
from .. import app, db_
import pandas as pd

start_date = "2022-11-01"
end_date = "2022-11-25"

with app.app_context():
    q = db_.engine.execute(
        f"""
        SELECT chart_date, gender, count(gender) FROM chart
        LEFT JOIN song ON song.song_spotify_id=chart.song_spotify_id
        LEFT JOIN artist ON song.artist_spotify_id=artist.spotify_id
        WHERE chart_date >= '{start_date}'
        AND chart_date < '{end_date}'
        GROUP BY chart_date, gender
        """
    ).all()
    df = pd.DataFrame(q)

fig = px.line(df, x="chart_date", y="count", color='gender')
fig.show()