from rcg import app_, db_
from rcg.db.models import Artist, ArtistSchema
from rcg.db.routes import get_new_chart
import os
import click
from dotenv import load_dotenv


@click.group()
def tools():
    pass

@tools.command()
def reset():
    """reset the rcg database"""
    if os.path.exists('./rcg/config/app.db'):
        os.remove('./rcg/config/app.db')

    db_.drop_all()
    db_.create_all()
    click.echo("db reset")
    return

@tools.command()
def create():
    """initialize the rcg database"""
    db_.create_all()
    click.echo("db created")
    return

@tools.command()
def update():
    """adds new rcg data if it exists"""
    output = get_new_chart()
    click.echo('db updated')
    return output

@tools.command()
@click.option("-a", "--artist")
@click.option("-g", "--gender")
def gender(artist, gender):
    Artist.query.filter_by(artist_name=f'{artist}').update(dict(gender=f"{gender}")) 
    db_.session.commit()
    click.echo(f'{artist} gender is now {gender}')
    return

if __name__=="__main__":
    load_dotenv()
    with app_.app_context():
        tools()
