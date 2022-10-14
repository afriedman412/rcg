from flask import Blueprint
from sqlalchemy import func
from collections import Counter
from ..code.helpers import get_date
from .. import db_
from .models import Artist, ChartEntry, Song, ArtistSchema, SongSchema, ChartEntrySchema

db_routes = Blueprint("db_routes", __name__)

nav_key = {
    'artist': (Artist, ArtistSchema()),
    'song': (Song, SongSchema())
}

@db_routes.route("/rcg/count/", methods=["GET"])
def get_counts():
    chart_date = get_date()
    q = db_.session.query(ChartEntry.chart_date, Song.song_name, Artist.artist_name, Artist.gender).join(
        Song, ChartEntry.song_spotify_id==Song.song_spotify_id
    ).outerjoin(
        Artist, Song.artist_spotify_id==Artist.artist_spotify_id
    ).filter(
        ChartEntry.chart_date==chart_date
    ).all()
    return Counter([s[3] for s in q])

@db_routes.route("/rcg/count/<g>", methods=["GET"])
def get_gender(g):
    chart_date = get_date()
    q = db_.session.query(ChartEntry.chart_date, Song.song_name, Artist.artist_name, Artist.gender).join(
        Song, ChartEntry.song_spotify_id==Song.song_spotify_id
    ).outerjoin(
        Artist, Song.artist_spotify_id==Artist.artist_spotify_id
    ).filter(
        ChartEntry.chart_date==chart_date
    ).filter(
        Artist.gender==g
        ).all()
    return Counter([s[2] for s in q])

@db_routes.route("/rcg/<table>/<id>", methods=["GET"])
def get_entry(table, id):
    Table, schema = tuple(nav_key.get(table))
    entry = Table.query.get(id)
    print(entry)
    return schema.jsonify(entry)

# get most recent chart
@db_routes.route("/rcg/chart/", methods=["GET"])
def get_recent_chart():
    max_chart_date = db_.session.query(func.max(ChartEntry.chart_date)).scalar()
    entries = db_.session.query(ChartEntry).filter(ChartEntry.chart_date==max_chart_date).all()
    schema = ChartEntrySchema(many=True)
    return schema.jsonify(entries)
    