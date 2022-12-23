from datetime import datetime as dt
import pandas as pd
from pandas import DataFrame
from typing import Tuple
from ..db import db_query

def parse_track(t):
    song_name, song_spotify_id, artists = (t)
    primary_artist_name, primary_artist_spotify_id = (artists[0])
    return song_name, song_spotify_id, artists, primary_artist_name, primary_artist_spotify_id

def parse_genders(l, w):
    try:
        return next(iter({l,w}.intersection('mf')))
    except StopIteration:
        if l == 'n' or w == 'n':
            return 'n'
        else:
            return 'x'

def get_date():
    day = dt.now()
    return day.strftime("%Y-%m-%d")

def get_recent_chart():
    date_ = get_date()
    q = f"""
        SELECT * FROM chart WHERE chart_date = "{date_}"
        """
    return db_query(q)

def get_counts():
    date_ = get_date()
    q = f"""
        SELECT gender, count(*)
        FROM chart
        LEFT JOIN song on chart.song_spotify_id=song.song_spotify_id
        LEFT JOIN artist on song.artist_spotify_id = artist.spotify_id
        WHERE chart_date = "{date_}"
        GROUP BY gender;
        """
    output = db_query(q)
    return output

def load_rap_caviar(sp):
    """
    TODO: is this redundant?
    """
    rc = sp.playlist('spotify:user:spotify:playlist:37i9dQZF1DX0XUsuxWHRQd')
    all_tracks = [
        (p['track']['name'], p['track']['id'], 
        [(a['name'], a['id']) for a in p['track']['artists']]) for p in rc['tracks']['items']
        ]
    return all_tracks

def load_chart(chart_date: str=None) -> Tuple[DataFrame, str]:
    """
    TODO: this is redundant!

    Loads the latest Rap Caviar chart from the db.
    TODO: should be able to do this live as well!!
    
    Assumes largest chart_date is latest chart if no chart_date provided.
    """
    q = """
        SELECT chart.song_name, chart.primary_artist_name, chart_date, artist.artist_name, gender
        FROM chart
        INNER JOIN song ON chart.song_spotify_id=song.song_spotify_id
        LEFT JOIN artist ON song.artist_spotify_id=artist.spotify_id
        """

    if not chart_date:
        q += """
            WHERE chart_date=(SELECT max(chart_date) FROM chart)
            """
            
    else:
        q += f"""
            WHERE chart_date='{chart_date}'
            """

    # do we need pandas?
    full_chart = pd.DataFrame(
        db_query(q), 
        columns=['song_name', 'primary_artist_name', 'chart_date', 'artist_name', 'gender'])

    full_chart['gender'] = full_chart['gender'].map({"m": "Male", "f": "Female", "n": "Non-Binary"})
    if not chart_date:
        chart_date = full_chart['chart_date'][0]
    chart_date = dt.strptime(chart_date, "%Y-%m-%d").strftime("%B %d, %Y")
    return full_chart, chart_date