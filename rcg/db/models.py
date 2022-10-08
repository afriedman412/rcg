from .. import db_, ma_
from ..code.helpers import parse_genders

class Song(db_.Model):
    __tablename__ = 'song'
    id = db_.Column("id", db_.Integer, primary_key=True)
    song_spotify_id = db_.Column("song_spotify_id", db_.String(240))
    song_name = db_.Column("song_name", db_.String(100))
    artist_spotify_id = db_.Column("artist_spotify_id", db_.String(240), db_.ForeignKey("artist.spotify_id"))
    artist_name = db_.Column(db_.String(100))
    primary = db_.Column(db_.Boolean)

    def __repr__(self):
        return f'<{self.__tablename__.title()} {self.song_name}>'

    def __init__(self, song_name, song_spotify_id, artist_name, artist_spotify_id, primary=False):
        self.song_name = song_name
        self.song_spotify_id = song_spotify_id
        self.artist_name = artist_name
        self.artist_spotify_id = artist_spotify_id
        self.primary = primary

class Artist(db_.Model):
    __tablename__ = 'artist'
    id = db_.Column(db_.Integer, primary_key=True)
    artist_spotify_id = db_.Column("spotify_id", db_.String(240), unique=True)
    artist_name = db_.Column("artist_name", db_.String(100), unique=True)
    # TODO: add validation for genders
    last_fm_gender = db_.Column("last_fm_gender", db_.String(1)) 
    wikipedia_gender = db_.Column("wikipedia_gender", db_.String(1))
    gender = db_.Column("gender", db_.String(1))
    songs = db_.relationship(
        'Song', backref='song', cascade='all, delete, delete-orphan',
        single_parent=True)

    def __repr__(self):
        return f'<{self.__tablename__.title()} {self.artist_name}>'

    def __init__(self, artist_name, artist_spotify_id, last_fm_gender, wikipedia_gender):
        self.artist_name = artist_name
        self.artist_spotify_id = artist_spotify_id
        self.last_fm_gender = last_fm_gender
        self.wikipedia_gender = wikipedia_gender
        self.gender = parse_genders(last_fm_gender, wikipedia_gender)

class ChartEntry(db_.Model):
    __tablename__ = 'chart'
    id = db_.Column(db_.Integer, primary_key=True)
    song_name = db_.Column(db_.String(240))
    song_spotify_id = db_.Column(db_.String(32))
    primary_artist_name = db_.Column(db_.String(32))
    primary_artist_spotify_id = db_.Column(db_.String(240))
    chart_date = db_.Column(db_.String(32)) # TODO: improve

    def __init__(self, song_name, song_spotify_id, chart_date, primary_artist_name, primary_artist_spotify_id):
        self.song_name = song_name
        self.song_spotify_id = song_spotify_id
        self.primary_artist_name = primary_artist_name
        self.primary_artist_spotify_id = primary_artist_spotify_id
        self.chart_date = chart_date

class ArtistSchema(ma_.Schema):
    class Meta:
        model = Artist
        sqla_session = db_.session
        fields = ('id', 'artist_name', 'artist_spotify_id', 'last_fm_gender', 'wikipedia_gender', 'gender')

class SongSchema(ma_.Schema):
    class Meta:
        model = Song
        sqla_session = db_.session
        fields = ('id', 'song_name', 'song_spotify_id', 'artist_name', 'artist_spotify_id', 'primary')

class ChartEntrySchema(ma_.Schema):
    class Meta:
        model = ChartEntry
        sqla_session = db_.session
        fields = ('id', 'chart_date', 'song_name', 'primary_artist_name')