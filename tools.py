import click
import os
from rcg.db import db_commit
from dotenv import load_dotenv
from rcg import app
from rcg.code.helpers import get_date, get_counts, get_chart_from_db, parse_track
from rcg.code.code import ChartLoader

@click.group()
@click.option("-l", "--local", is_flag=True)
def tools(local):
    if local:
        os.environ['LOCAL'] = "True"
    load_dotenv()
    pass

@tools.command()
def current():
    chart = get_chart_from_db()
    click.echo(chart)
    return

@tools.command()
def count():
    """
    Returns gender counts for current chart.
    """
    with app.app_context():
        c = get_counts()
        click.echo(c)
    return

@tools.command()
def current_rc():
    """
    Returns the rap caviar chart from Spotify.
    """
    cl = ChartLoader()
    chart = cl.load_rap_caviar()
    for c in chart:
        click.echo(c)
    return

@tools.command()
def xday():
    """
    Deletes the chart for the current day.
    """
    chart_date = get_date()
    q = f"""
        DELETE FROM chart
        WHERE chart_date='{chart_date}'
        """
    db_commit(q)
    click.echo(f"{chart_date} data deleted")
    return

@tools.command()
def update():
    """adds new rcg data if it exists"""
    cl = ChartLoader()
    output = cl.update_chart()
    click.echo('db updated')
    return output

@tools.command()
@click.option("-s", "--song_spotify_id")
def add_artists(song_spotify_id: str):
    """
    Adds all artists for a song_spotify_id to the db.
    """
    cl = ChartLoader()
    t = cl.sp.track(song_spotify_id)
    t = parse_track(t)
    print(t)
    cl.add_all_info_from_one_track(t, False)
    return


@tools.command()
@click.option("-a", "--artist")
@click.option("-g", "--gender")
def gender(artist, gender):
    """
    Sets artist's gender.
    """
    q = f"""
    UPDATE artist
    SET gender="{gender}"
    WHERE artist_name="{artist}";
    """
    db_commit(q)
    click.echo(f'{artist} gender is now {gender}')
    return

if __name__=="__main__":
    
    tools()
    
        
