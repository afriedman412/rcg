from flask import Blueprint, request
from sqlalchemy import func
from ..code.helpers import gender_count, parse_track, get_week_start
from .. import db_, dh_
from .models import Artist, ChartEntry, Song, ArtistSchema, SongSchema, ChartEntrySchema

db_routes = Blueprint("db_routes", __name__)

nav_key = {
    'artist': (Artist, ArtistSchema()),
    'song': (Song, SongSchema())
}

@db_routes.route("/rcg/<data_type>", methods=["POST"])
def new_entry(data_type):
    lfm = dh_.lfm_network
    Table, schema = tuple(nav_key.get(data_type))
    name = request.json['name']

    if data_type == 'song':
        song_spotify_id = request.json['song_spotify_id']
        artist_spotify_id = request.json['artist_spotify_id']
        new_entry = Table(song_spotify_id, name, artist_spotify_id,)

    elif data_type == 'artist':
        wikipedia_gender = gender_count(name)
        lfm_gender = gender_count(name, lastfm_network=lfm)

        new_entry = Table(name, lfm_gender, wikipedia_gender)

    db_.session.add(new_entry)
    db_.session.commit()
    return schema.jsonify(new_entry)

@db_routes.route("/rcg/<table>/<id>", methods=["GET"])
def get_entry(table, id):
    Table, schema = tuple(nav_key.get(table))
    entry = Table.query.get(id)
    print(entry)
    return schema.jsonify(entry)

# add new chart
@db_routes.route("/rcg/chart/new/", methods=["POST"])
def get_new_chart():
    lfm = dh_.lfm_network
    all_tracks = dh_.load_rap_caviar()
    new_entries = []
    chart_date = get_week_start()

    # verify chart has changed
    q = db_.session.query(ChartEntry).filter(
        ChartEntry.chart_date==chart_date
    ).all()
    if {q_.song_spotify_id for q_ in q} == {t[1] for t in all_tracks}:
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

        primary = True # only the first artist is the primary
        for a in artists:
            # add artists
            name, artist_spotify_id = a
            check = db_.session.query(Artist).filter_by(artist_name=f"{name}").first()
            print(check)
            if not check:
                lfm_gender = gender_count(name, lastfm_network=lfm)
                wikipedia_gender = gender_count(name)

                artist_entry = Artist(
                    name, artist_spotify_id, lfm_gender, wikipedia_gender)
                db_.session.add(artist_entry)

            # add song/artist relationships
            song_artist_entry = Song(
                song_spotify_id = song_spotify_id,
                song_name = song_name,
                artist_spotify_id = artist_spotify_id,
                artist_name = name,
                primary = primary
            )
            primary = False
            db_.session.add(song_artist_entry)

        db_.session.commit()
        new_entries.append(chart_entry)

    schema = ChartEntrySchema(many=True)
    return schema.jsonify(new_entries)

# get most recent chart
@db_routes.route("/rcg/chart/", methods=["GET"])
def get_recent_chart():
    max_chart_date = db_.session.query(func.max(ChartEntry.chart_date)).scalar()
    entries = db_.session.query(ChartEntry).filter(ChartEntry.chart_date==max_chart_date).all()
    schema = ChartEntrySchema(many=True)
    return schema.jsonify(entries)

# fix artist gender
@db_routes.route("/rcg/gupdate/<a>/<g>", methods=["POST"])
def update_gender(a, g):
    Artist.query.filter_by(artist_name=f'{a}').update(dict(gender=f"{g}")) 
    db_.session.commit()

    new_artist_entry = db_.session.query(Artist).filter(Artist.artist_name==f"{a}").first()
    schema = ArtistSchema()
    return schema.jsonify(new_artist_entry)
    