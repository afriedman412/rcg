import pylast
import wikipedia
from collections import Counter
import spotipy
from .helpers import get_date, parse_track
from ..db.models import ChartEntry, ChartEntrySchema, Artist, Song

class Creds:
    """
    Credential manager for spotify and lastfm, also used to load the actual playlist from spotify.
    """
    def __init__(self, app):
        self.reset_credentials(app)
        return

    def reset_credentials(self, app):
        self.sp = self.access_spotify(app)
        self.lfm_network = self.access_lfm(app)

    def access_lfm(self, app):
        return pylast.LastFMNetwork(
            api_key=app.config['LAST_FM_ID'],
            api_secret=app.config['LAST_FM_SECRET'],
            username=app.config['LAST_FM_USER'],
            password_hash=pylast.md5(app.config['LAST_FM_PW'])
        )

    def access_spotify(self, app):
        spotify_cred_manager = spotipy.oauth2.SpotifyClientCredentials(
            app.config['SPOTIFY_ID'], 
            app.config['SPOTIFY_SECRET']
            )
        return spotipy.Spotify(client_credentials_manager=spotify_cred_manager)

class ChartLoader(Creds):
    def __init__(self, app):
        super(ChartLoader, self).__init__(app) # TODO: better credential storage than app
        return

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

def get_new_chart(db_, dh_: Creds): # TODO: chart object should be a class, probably
    """
    Loads latest Rap Caviar data and does all requisite processing.
    """
    lfm = dh_.lfm_network
    all_tracks = dh_.load_rap_caviar()
    new_entries = []
    chart_date = get_date()

    # verify chart has changed
    q = db_.session.query(ChartEntry).filter(ChartEntry.chart_date==chart_date).all()
    if {q_.song_spotify_id for q_ in q} == {t[1] for t in all_tracks}:
        print(f"no updates, chart date {chart_date}")
        return {"status": "no update for chart date"}

    for t in all_tracks:
        song_name, song_spotify_id, artists, primary_artist_name, primary_artist_spotify_id = parse_track(t)

        # add chart entry
        chart_entry = ChartEntry(
            song_name = song_name,
            song_spotify_id = song_spotify_id,
            primary_artist_name = primary_artist_name,
            primary_artist_spotify_id = primary_artist_spotify_id,
            chart_date = chart_date
        )
        db_.session.add(chart_entry)
        db_.session.commit()

        primary = True # only the first artist is the primary
        for a in artists:
            # add artists
            name, artist_spotify_id = a
            artist_check = db_.session.query(Artist).filter_by(artist_spotify_id=f"{artist_spotify_id}").first()
            if not artist_check:
                print(f"adding {name} to artists")
                lfm_gender = gender_count(name, lastfm_network=lfm)
                wikipedia_gender = gender_count(name)

                artist_entry = Artist(
                    name, artist_spotify_id, lfm_gender, wikipedia_gender)
                db_.session.add(artist_entry)
                db_.session.commit()

            # add song/artist relationships
            song_check = db_.engine.execute(
                f"""
                SELECT * FROM song 
                WHERE song_spotify_id = '{song_spotify_id}'
                AND artist_spotify_id = '{artist_spotify_id}'
                """
            ).first()
            if not song_check:
                print(f"adding {name} on {song_name}")
                song_artist_entry = Song(
                    song_spotify_id = song_spotify_id,
                    song_name = song_name,
                    artist_spotify_id = artist_spotify_id,
                    artist_name = name,
                    primary = primary
                )
                db_.session.add(song_artist_entry)
                db_.session.commit()
            primary = False # no matter what, first artist is primary
        
        new_entries.append(chart_entry)

    print(f"chart date updated for {chart_date}")
    schema = ChartEntrySchema(many=True)
    return schema.jsonify(new_entries)
