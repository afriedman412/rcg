from rcg import app_, db_
from rcg.db.models import Artist
from rcg.db.routes import get_new_chart, get_counts, get_week_start
import os
import click
from dotenv import load_dotenv


@click.group()
@click.option("-l", "--local", is_flag=True)
@click.option("-s", "--silence", is_flag=True)
def tools(local, silence):
    load_dotenv()
    if local:
        app_.SQLALCHEMY_DATABASE_URI = "postgresql:///rcg"
    if silence:
        app_.SQLALCHEMY_ECHO = False
    pass

@tools.command()
def count():
    with app_.app_context():
        c = get_counts()
        click.echo(c)
    return

@tools.command()
def xweek():
    chart_date = get_week_start()
    with app_.app_context():
        db_.engine.execute(
            f"""
            DELETE FROM chart
            WHERE chart_date='{chart_date}'
            """
        )
    click.echo(f"{chart_date} data deleted")
    return

@tools.command()
def reset():
    """reset the rcg database"""
    if os.path.exists('./rcg/config/app.db'):
        os.remove('./rcg/config/app.db')
    with app_.app_context():
        db_.drop_all()
        db_.create_all()
        click.echo("db reset")
    return

@tools.command()
def create():
    """initialize the rcg database"""
    with app_.app_context():
        db_.create_all()
        click.echo("db created")
    return

@tools.command()
def update():
    """adds new rcg data if it exists"""
    with app_.app_context():
        output = get_new_chart()
        click.echo('db updated')
    return output

@tools.command()
@click.option("-a", "--artist")
@click.option("-g", "--gender")
def gender(artist, gender):
    with app_.app_context():
        Artist.query.filter_by(artist_name=f'{artist}').update(dict(gender=f"{gender}")) 
        db_.session.commit()
        click.echo(f'{artist} gender is now {gender}')
    return

if __name__=="__main__":
    tools()
    
        
