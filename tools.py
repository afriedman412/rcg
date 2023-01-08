"""
Inconsistant implementation of local/remote db control. Sometimes you can control it and sometimes you can't. That's probably fine, because the default is "LOCAL" environmental variable. But it's bad form.
"""

import click
from rcg.db import db_commit, db_query
from dotenv import load_dotenv
from rcg import app
from rcg.code.helpers import get_date, get_counts, get_chart_from_db, parse_track, chart_date_check
from rcg.code.code import ChartLoader

@click.group()
@click.option("-l", "--local", is_flag=True)
@click.pass_context
def tools(ctx, local):
    ctx.ensure_object(dict)
    print(f"** Tools USING {'LOCAL' if local else 'REMOTE'} **")
    ctx.obj['LOCAL'] = local
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
@click.pass_context
def xday(ctx):
    """
    Deletes the chart for the current day.
    """
    chart_date = get_date()
    q = f"""
        DELETE FROM chart
        WHERE chart_date='{chart_date}'
        """
    db_commit(q, ctx.obj['LOCAL'])
    print("max date:", chart_date_check(ctx.obj['LOCAL']))
    click.echo(f"{chart_date} data deleted")
    return

@tools.command()
@click.pass_context
def update(ctx):
    """adds new rcg data if it exists"""
    cl = ChartLoader(ctx.obj['LOCAL'])
    output = cl.update_chart()
    if output:
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
@click.pass_context
def gender(ctx, artist, gender):
    """
    Sets artist's gender.
    """
    q = f"""
    UPDATE artist
    SET gender="{gender}"
    WHERE artist_name="{artist}";
    """
    db_commit(q, ctx.obj["LOCAL"])
    click.echo(f'{artist} gender is now {gender}')
    return

@tools.command()
@click.pass_context
def ctxtest(ctx):
    print(ctx.obj['LOCAL'])
    q = "select min(chart_date) from chart"
    print(db_query(q, ctx.obj["LOCAL"]))
    return

if __name__=="__main__":
    tools()
    
        
