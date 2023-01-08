"""
Inconsistant implementation of local/remote db control. Sometimes you can control it and sometimes you can't. That's probably fine, because the default is "LOCAL" environmental variable. But it's bad form.
"""

import pylast
import os
import wikipedia
from typing import Tuple
from collections import Counter
import spotipy
from ..db import db_commit, db_query
from .helpers import (
    get_date, 
    parse_track, 
    parse_genders, 
    get_chart_from_db, 
    chart_date_check
    )

class Creds:
    """
    Credential manager for spotify and lastfm, also used to load the actual playlist from spotify.

    Relies on environment, not app. No need to pass it anything, assuming dotenv loaded correctly.
    """
    def __init__(self):
        """
        Loads credentials on init.
        """
        self.reset_credentials()
        return

    def reset_credentials(self):
        self.sp = self.access_spotify()
        self.lfm_network = self.access_lfm()

    def access_lfm(self):
        return pylast.LastFMNetwork(
            api_key=os.environ['LAST_FM_ID'],
            api_secret=os.environ['LAST_FM_SECRET'],
            username=os.environ['LAST_FM_USER'],
            password_hash=pylast.md5(os.environ['LAST_FM_PW'])
        )

    def access_spotify(self):
        spotify_cred_manager = spotipy.oauth2.SpotifyClientCredentials(
            os.environ['SPOTIFY_ID'], 
            os.environ['SPOTIFY_SECRET']
            )
        return spotipy.Spotify(client_credentials_manager=spotify_cred_manager)

class ChartLoader(Creds):
    def __init__(self, local: bool=False):
        super(ChartLoader, self).__init__()
        self.chart_date = get_date()
        self.local = local
        print(f"***** ChartLoader USING {'LOCAL' if self.local else 'REMOTE'} DB *****")
        return

    def load_rap_caviar(self):
        """
        Loads the current rap caviar playlist from Spotify.
        """
        rc = self.sp.playlist('spotify:user:spotify:playlist:37i9dQZF1DX0XUsuxWHRQd')
        all_tracks = [parse_track(t['track']) for t in rc['tracks']['items']]
        return all_tracks

    def compare_charts(self):
        """
        Compares the current rap caviar chart to the latest chart in the db.

        Returns False if they are the same, returns the current chart if they aren't.
        """
        current_chart = self.load_rap_caviar()
        latest_chart = get_chart_from_db()

        if {t[2] for t in latest_chart} == {t[1] for t in current_chart} \
            and get_date() == chart_date_check(self.local):
                print(f"no updates, chart date {self.chart_date}")
                return False
        else:
            print(f"updating chart for {self.chart_date}")
            return current_chart

    def artist_check(self, artist_spotify_id: str):
        """
        Is artist_spotify_id in the db?
        """
        return db_query(f'SELECT * from artist where spotify_id="{artist_spotify_id}"', self.local)

    def gender_parse(self, artist_name: str) -> Tuple[str]:
        """
        Gets the gender from last.fm and wikipedia, then determines the "official" gender.

        Returns all three.
        """
        lfm_gender = self.gender_count(artist_name, lastfm_network=self.lfm_network)
        wikipedia_gender = self.gender_count(artist_name)
        gender = parse_genders(lfm_gender, wikipedia_gender)
        return lfm_gender, wikipedia_gender, gender

    def chart_song_check(self, song_spotify_id, primary_artist_spotify_id):
        """
        Is the song song_spotify_id by artist_spotify_id already in the current chart?
        """
        return db_query(
                    f"""
                    SELECT * FROM chart 
                    WHERE song_spotify_id="{song_spotify_id}"
                    AND primary_artist_spotify_id="{primary_artist_spotify_id}"
                    AND chart_date="{self.chart_date}";
                    """,
                self.local
                )

    def song_check(self, song_spotify_id, artist_spotify_id):
        """
        Is the song song_spotify_id by artist_spotify_id in the db?

        Probably redundant to do both, but extra careful!
        """
        return db_query(
                    f"""
                    SELECT * FROM song 
                    WHERE song_spotify_id="{song_spotify_id}"
                    AND artist_spotify_id="{artist_spotify_id}"; 
                    """,
                    self.local
                )

    def add_all_info_from_one_track(self, t: tuple, add_to_chart: bool=True):
        """
        Adds the track to the db (chart table), then adds any artists that aren't already in the db, and adds the song if it's not already in the db (song table).
        """
        song_name, song_spotify_id, artists, primary_artist_name, primary_artist_spotify_id = (t)

        if add_to_chart:
            if not self.chart_song_check(song_spotify_id, primary_artist_spotify_id):
                q = """
                    INSERT INTO 
                    chart (song_name, song_spotify_id, primary_artist_name, 
                    primary_artist_spotify_id, chart_date)
                    VALUES (""" + ", ".join(
                    f'"{p}"' for p in 
                    [song_name, song_spotify_id, primary_artist_name, primary_artist_spotify_id, self.chart_date
                    ]) + ");"

                db_commit(q, self.local)

        primary = True # only the first artist is the primary
        for a in artists:
            artist_name, artist_spotify_id = a
            if not self.artist_check(artist_spotify_id):
                print(f"adding {artist_name} to artists")
                lfm_gender, wikipedia_gender, gender = self.gender_parse(artist_name)
                q = """
                    INSERT INTO 
                    artist (spotify_id, artist_name, last_fm_gender, 
                    wikipedia_gender, gender)
                    VALUES (""" + ", ".join(
                    f'"{p}"' for p in 
                    [artist_spotify_id, artist_name, lfm_gender, wikipedia_gender, gender]) + ");"
                db_commit(q, self.local)

            if not self.song_check(song_spotify_id, artist_spotify_id):
                q = f"""
                    INSERT INTO 
                    song (song_name, song_spotify_id, artist_name, artist_spotify_id, `primary`)
                    VALUES (""" + ", ".join(
                    f'"{p}"' for p in 
                    [song_name, song_spotify_id, artist_name, artist_spotify_id, primary]) + ");"
                db_commit(q, self.local)
            primary=False
        return

    def update_chart(self):
        """
        Does all steps for adding the latest chart.
        """
        newest_chart = self.compare_charts()
        if newest_chart:
            for t in newest_chart:
                self.add_all_info_from_one_track(t)
            print(f"chart date updated for {self.chart_date}")

            q = f"""
                SELECT * FROM chart WHERE chart_date = "{self.chart_date}"
                """
            return db_query(q, self.local)
        else:
            return

    def gender_count(self, artist: str, lastfm_network=None, return_counts: bool=False) -> int:
        """
        Counts pronouns in either lastfm or wikipedia bio to make best guess at gender.

        lastfm_network is the source switch -- if no last fm network is provided, uses wikipedia.
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


