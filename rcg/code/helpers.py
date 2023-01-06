from datetime import datetime as dt
import pandas as pd
from pandas import DataFrame
import os
from typing import Tuple
from ..db import db_query

def parse_track(t):
    """
    Unpacks track metadata from a Spotify track.
    """
    song_name, song_spotify_id, artists = (t['name'], t['id'], [(a['name'], a['id']) for a in t['artists']])
    primary_artist_name, primary_artist_spotify_id = (artists[0])
    return song_name, song_spotify_id, artists, primary_artist_name, primary_artist_spotify_id

def parse_genders(l, w) -> str:
    """
    Logic to decide which gender to return (m, f, n, or x)

    'm' or 'f' if either is present at all, 'n' if either is 'n', otherwise 'x'.
    """
    try:
        return next(iter({l,w}.intersection('mf')))
    except StopIteration:
        if l == 'n' or w == 'n':
            return 'n'
        else:
            return 'x'

def get_date() -> str:
    """
    Gets today and turns it into a string.
    """
    day = dt.now()
    return day.strftime("%Y-%m-%d")

def query_w_date(q: str, date_: str=None):
    """
    Easier to make this a function than to do the date logic every time.
    """
    if not date_:
        date_ = get_date()
    return db_query(q.format(date_))

def get_chart_from_db(date_: str=None):
    q = """
        SELECT * FROM chart WHERE chart_date = "{}"
        """
    return query_w_date(q, date_)

def get_counts(date_: str=None):
    q = """
        SELECT gender, count(*)
        FROM chart
        LEFT JOIN song on chart.song_spotify_id=song.song_spotify_id
        LEFT JOIN artist on song.artist_spotify_id = artist.spotify_id
        WHERE chart_date = "{}"
        GROUP BY gender;
        """
    return query_w_date(q, date_)

def load_chart(chart_date: str=None) -> Tuple[DataFrame, str]:
    """
    Loads the latest Rap Caviar chart from the db and returns it as a DataFrame.

    Assumes largest chart_date is latest chart if no chart_date provided.

    TODO: is this redundant, do we need this, does it have to be pandas?
    """
    chart_date = os.environ['CHART_DATE'] if not chart_date else chart_date
    chart_date = dt.strptime(chart_date, "%Y-%m-%d").strftime("%Y-%m-%d")

    q = f"""
        SELECT chart.song_name, chart.primary_artist_name, chart_date, artist.artist_name, gender
        FROM chart
        INNER JOIN song ON chart.song_spotify_id=song.song_spotify_id
        LEFT JOIN artist ON song.artist_spotify_id=artist.spotify_id
        WHERE chart_date="{chart_date}"
        """

    # if not chart_date:
    #     chart_date = os.environ['CHART_DATE']
    #     q += """
    #         WHERE chart_date=(SELECT max(chart_date) FROM chart)
    #         """
            
    # else:
        # chart_date = dt.strptime(chart_date, "%Y-%m-%d").strftime("%Y-%m-%d")
        # q += f"""
        #     WHERE chart_date="{chart_date}"
        #     """

    full_chart = pd.DataFrame(
        db_query(q), 
        columns=['song_name', 'primary_artist_name', 'chart_date', 'artist_name', 'gender'])
    full_chart['gender'] = full_chart['gender'].map({"m": "Male", "f": "Female", "n": "Non-Binary"})
    if not chart_date:
        chart_date = full_chart['chart_date'][0]
    formatted_chart_date = dt.strptime(chart_date, "%Y-%m-%d").strftime("%B %-d, %Y")
    return full_chart, formatted_chart_date