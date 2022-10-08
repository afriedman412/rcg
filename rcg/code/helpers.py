import pylast
import wikipedia
from collections import Counter
import spotipy
from datetime import datetime as dt
from datetime import timedelta

class DataHandler:
    def __init__(self, app):
        self.reset_credentials(app)
        return

    def reset_credentials(self, app):
        spotify_cred_manager = spotipy.oauth2.SpotifyClientCredentials(
            app.config['SPOTIFY_ID'], 
            app.config['SPOTIFY_SECRET']
            )
        self.sp = spotipy.Spotify(client_credentials_manager=spotify_cred_manager)

        self.lfm_network = pylast.LastFMNetwork(
            api_key=app.config['LAST_FM_ID'],
            api_secret=app.config['LAST_FM_SECRET'],
            username=app.config['LAST_FM_USER'],
            password_hash=pylast.md5(app.config['LAST_FM_PW'])
        )
    
    def load_rap_caviar(self):
        rc = self.sp.playlist('spotify:user:spotify:playlist:37i9dQZF1DX0XUsuxWHRQd')
        all_tracks = [
            (p['track']['name'], p['track']['id'], 
            [(a['name'], a['id']) for a in p['track']['artists']]) for p in rc['tracks']['items']
            ]
        return all_tracks

def gender_count(artist, lastfm_network=None, return_counts=False):
    """
    If no last fm network is provided, use wikipedia.
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
        
    bio = Counter(bio.split())
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

def get_week_start(day: dt=None):
    if not day:
        day = dt.now()
    week_start = day.date() - timedelta(day.weekday())
    return week_start.strftime("%Y-%m-%d")
