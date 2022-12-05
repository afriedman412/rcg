from flask import Blueprint, jsonify
from ..code.helpers import get_date
from . import db_query

db_routes = Blueprint("db_routes", __name__)

@db_routes.route("/rcg/count/", methods=["GET"])
def get_counts():
    date_ = get_date()
    q = f"""
        SELECT gender, count(*)
        FROM chart
        LEFT JOIN song on chart.song_spotify_id=song.song_spotify_id
        LEFT JOIN artist on song.artist_spotify_id = artist.spotify_id
        WHERE chart_date = "{date_}"
        GROUP BY gender;
        """
    return jsonify(db_query(q), 200)

@db_routes.route("/rcg/count/<g>", methods=["GET"])
def get_gender(g):
    date_ = get_date()
    q = f"""
        SELECT count(*)
        FROM chart
        LEFT JOIN song on chart.song_spotify_id=song.song_spotify_id
        LEFT JOIN artist on song.artist_spotify_id = artist.spotify_id
        WHERE chart_date="{date_}"
        AND gender="{g}";
        """
    return jsonify(db_query(q), 200)

@db_routes.route("/rcg/<table>/<id>", methods=["GET"])
def get_entry(table, id):
    q = f"""
    SELECT * FROM {table} WHERE ID={id}
    """
    return jsonify(db_query(q), 200)

@db_routes.route("/rcg/chart/", methods=["GET"])
def get_recent_chart():
    date_ = get_date()
    q = f"""
        SELECT * FROM chart WHERE chart_date = "{date_}"
        """
    return jsonify(db_query(q), 200)