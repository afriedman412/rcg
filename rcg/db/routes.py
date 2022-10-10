from flask import Blueprint
from sqlalchemy import func
from collections import Counter
from ..code.helpers import gender_count, parse_track, get_week_start
from .. import db_, dh_
from .models import Artist, ChartEntry, Song, ArtistSchema, SongSchema, ChartEntrySchema

db_routes = Blueprint("db_routes", __name__)

nav_key = {
    'artist': (Artist, ArtistSchema()),
    'song': (Song, SongSchema())
}

@db_routes.route("/rcg/count/", methods=["GET"])
def get_counts():
    chart_date = get_week_start()
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
    chart_date = get_week_start()
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

# get new chart
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

# get most recent chart
@db_routes.route("/rcg/chart/", methods=["GET"])
def get_recent_chart():
    max_chart_date = db_.session.query(func.max(ChartEntry.chart_date)).scalar()
    entries = db_.session.query(ChartEntry).filter(ChartEntry.chart_date==max_chart_date).all()
    schema = ChartEntrySchema(many=True)
    return schema.jsonify(entries)
    