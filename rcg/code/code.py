import pylast
import wikipedia
from collections import Counter
import spotipy
import os
from .helpers import get_date, parse_track, parse_genders, load_rap_caviar, get_recent_chart
from ..db import db_commit, db_query

class Creds:
    """
    Credential manager for spotify and lastfm, also used to load the actual playlist from spotify.
    """
    def __init__(self):
        self.reset_credentials()
        return

    def reset_credentials(self):
        self.sp = self.access_spotify()
        self.lfm_network = self.access_lfm()

    def access_lfm(self):
        return pylast.LastFMNetwork(
            api_key=os.environ.get('LAST_FM_ID'),
            api_secret=os.environ.get('LAST_FM_SECRET'),
            username=os.environ.get('LAST_FM_USER'),
            password_hash=pylast.md5(os.environ.get('LAST_FM_PW'))
        )

    def access_spotify(self):
        spotify_cred_manager = spotipy.oauth2.SpotifyClientCredentials(
            os.environ.get('SPOTIFY_ID'), 
            os.environ.get('SPOTIFY_SECRET')
            )
        return spotipy.Spotify(client_credentials_manager=spotify_cred_manager)

def gender_count(artist: str, lastfm_network=None, return_counts: bool=False) -> int:
    """
    Counts pronouns in either lastfm or wikipedia bio to make best guess at gender.

    If no last fm network is provided, uses wikipedia.
    """
    if lastfm_network:
        try:
            bio = pylast.Artist(artist, lastfm_network).get_bio_content(language="en")
            if (not bio) or (bio.startswith('<a href="https://www.last.fm/music/')):
                return "x" # no last fm bio
        except pylast.WSError:
            return "l" # artist not found in last fm
    else:
        try:
            bio = wikipedia.page(artist, auto_suggest=False, redirect=True).content
        except wikipedia.DisambiguationError as e:
            try:
                artist_ = next(o for o in e.options if 'rapper' in o)
                bio = wikipedia.page(artist_, auto_suggest=False, redirect=True).content
            except StopIteration:
                return "d" # disambiguation error
        except wikipedia.PageError:
            return "p" # page error
        
    bio = Counter(bio.lower().split())
    data = [
        ('m', ['he', 'him', 'his']),
        ('f', ['she', 'her', 'hers']),
        ('n', ['they', 'them', 'theirs'])
    ]
    counts = {d[0]:sum([bio[p] for p in d[1]]) for d in data}
    if return_counts:
        return counts
    else:
        return max(counts, key=counts.get)

def update_chart(creds: Creds): # TODO: chart object should be a class, probably
    """
    Loads latest Rap Caviar data and does all requisite processing.
    """
    lfm = creds.lfm_network
    sp = creds.access_spotify()
    newest_chart = load_rap_caviar(sp)
    chart_date = get_date()
    latest_chart = get_recent_chart()

    if {t[2] for t in latest_chart} == {t[1] for t in newest_chart}:
        print(f"no updates, chart date {chart_date}")
        return {"status": "no update for chart date"}

    for t in newest_chart:
        song_name, song_spotify_id, artists, primary_artist_name, primary_artist_spotify_id = parse_track(t)

        q = """
            INSERT INTO chart 
            (song_name, song_spotify_id, primary_artist_name, primary_artist_spotify_id, chart_date)
            VALUES (""" + ", ".join(f'"{p}"' for p in [
                song_name, 
                song_spotify_id, 
                primary_artist_name, 
                primary_artist_spotify_id, 
                chart_date
            ]) + ");"
        db_commit(q)

        primary = True # only the first artist is the primary
        for a in artists:
            # add artists
            artist_name, artist_spotify_id = a
            artist_check = db_query(f'SELECT * from artist where spotify_id="{artist_spotify_id}"')
            if not artist_check:
                print(f"adding {artist_name} to artists")
                lfm_gender = gender_count(artist_name, lastfm_network=lfm)
                wikipedia_gender = gender_count(artist_name)
                gender = parse_genders(lfm_gender, wikipedia_gender)

                q = """
                    INSERT INTO 
                    artist (artist_name, spotify_id, last_fm_gender, wikipedia_gender, gender)
                    VALUES (""" + ", ".join(
                    f'"{p}"' for p in [
                        artist_name, 
                        artist_spotify_id, 
                        lfm_gender, 
                        wikipedia_gender, 
                        gender
                        ]) + ");"

                db_commit(q)

            song_check = db_query(
                f"""
                SELECT * FROM song 
                WHERE song_spotify_id="{song_spotify_id}"
                AND artist_spotify_id="{artist_spotify_id}"; 
                """
                )

            if not song_check:
                q = """
                    INSERT INTO song 
                    (song_name, song_spotify_id, artist_name, artist_spotify_id, `primary`)
                    VALUES (""" + ", ".join(
                    f'"{p}"' for p in [
                        song_name, 
                        song_spotify_id, 
                        artist_name, 
                        artist_spotify_id, 
                        primary
                    ]) + ");"
                print(q)
                db_commit(q)

            primary = False # no matter what, first artist is primary
    

    print(f"chart date updated for {chart_date}")
    return
