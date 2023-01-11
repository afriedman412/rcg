from datetime import datetime as dt
import pandas as pd
from pandas import DataFrame
import os
from typing import Tuple
from pytz import timezone
import spotipy
from .track_code import Track
from ..db import db_query

def update_chart(local: bool=False):
    """
    Updates chart for current date. 
    """
    current_chart = load_rap_caviar()
    latest_chart = get_chart_from_db()
    chart_date = get_date()

    if {t[2] for t in latest_chart} == {t[1] for t in current_chart} \
        and get_date() == most_recent_chart_date(local):
            print(f"no updates, chart date {chart_date}")
            return False
    else:
        print(f"updating chart for {chart_date}")
        
        for t in current_chart:
            t = Track(t, chart_date) # parse_track is in load_rap_caviar
            t.update_chart()

        print(f"chart date updated for {chart_date}")

        q = f"""
            SELECT * FROM chart WHERE chart_date = "{chart_date}"
            """
        return db_query(q, local)

def most_recent_chart_date(local: bool=False) -> str:
    """
    Gets the most recent chart date.
    """
    checker = db_query("select max(chart_date) from chart", local)
    return checker[0][0]

def parse_track(t):
    """
    Unpacks track metadata from a Spotify track.
    """
    song_name, song_spotify_id, artists = (t['name'], t['id'], [(a['name'], a['id']) for a in t['artists']])
    primary_artist_name, primary_artist_spotify_id = (artists[0])
    return song_name, song_spotify_id, artists, primary_artist_name, primary_artist_spotify_id

def load_spotipy():
    """
    Instantiates Spotipy object w credentials.
    """
    spotify_cred_manager = spotipy.oauth2.SpotifyClientCredentials(
        os.environ['SPOTIFY_ID'], 
        os.environ['SPOTIFY_SECRET']
        )
    sp = spotipy.Spotify(client_credentials_manager=spotify_cred_manager)
    return sp

def load_rap_caviar():
    """
    Loads the current rap caviar playlist from Spotify.
    """
    sp = load_spotipy()
    rc = sp.playlist('spotify:user:spotify:playlist:37i9dQZF1DX0XUsuxWHRQd')
    current_chart = [parse_track(t['track']) for t in rc['tracks']['items']]
    return current_chart

def load_one_song(song_spotify_id: str):
    sp = load_spotipy()
    track_info = sp.track(song_spotify_id)
    track_info = parse_track(track_info)
    return track_info

def get_date() -> str:
    """
    Gets today for the Eastern time zone and turns it into a string.
    """
    day = timezone('US/Eastern').localize(dt.now())
    return day.strftime("%Y-%m-%d")

def query_w_date(q: str, date_: str=None, local: bool=False):
    """
    Easier to make this a function than to do the date logic every time.
    """
    if not date_:
        date_ = get_date()
    return db_query(q.format(date_), local)

def get_chart_from_db(date_: str=None, local: bool=False):
    q = """
        SELECT * FROM chart WHERE chart_date = "{}"
        """
    return query_w_date(q, date_, local)

def get_counts(date_: str=None, local: bool=False):
    q = """
        SELECT gender, count(*)
        FROM chart
        LEFT JOIN song on chart.song_spotify_id=song.song_spotify_id
        LEFT JOIN artist on song.artist_spotify_id = artist.spotify_id
        WHERE chart_date = "{}"
        GROUP BY gender;
        """
    return query_w_date(q, date_, local)

def load_chart(chart_date: str=None, local: bool=False) -> Tuple[DataFrame, str]:
    """
    Loads the chart from chart_date, defaulting to the latest chart in the db.
    
    Returns it as a DataFrame, formatted for Flask HTML processing.

    TODO: Does it have to be pandas?
    """
    chart_date = most_recent_chart_date() if not chart_date else chart_date
    chart_date = dt.strptime(chart_date, "%Y-%m-%d").strftime("%Y-%m-%d")

    q = f"""
        SELECT chart.song_name, chart.primary_artist_name, chart_date, artist.artist_name, gender
        FROM chart
        INNER JOIN song ON chart.song_spotify_id=song.song_spotify_id
        LEFT JOIN artist ON song.artist_spotify_id=artist.spotify_id
        WHERE chart_date="{chart_date}"
        """

    full_chart = pd.DataFrame(
        db_query(q, local), 
        columns=['song_name', 'primary_artist_name', 'chart_date', 'artist_name', 'gender'])
    full_chart['gender'] = full_chart['gender'].map({"m": "Male", "f": "Female", "n": "Non-Binary"})
    if not chart_date:
        chart_date = full_chart['chart_date'][0]
    formatted_chart_date = dt.strptime(chart_date, "%Y-%m-%d").strftime("%B %-d, %Y")
    return full_chart, formatted_chart_date