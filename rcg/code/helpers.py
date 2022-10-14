from datetime import datetime as dt
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