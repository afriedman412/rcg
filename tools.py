from rcg import app
from rcg.db import db_commit
from rcg.db.routes import get_counts
from rcg.code.helpers import get_date
from rcg.code.code import update_chart, Creds
import click
from dotenv import load_dotenv

@click.group()
@click.option("-l", "--local", is_flag=True)
@click.option("-s", "--silence", is_flag=True)
def tools(local, silence):
    load_dotenv()
    if local:
        app.SQLALCHEMY_DATABASE_URI = "postgresql:///rcg"
    if silence:
        app.SQLALCHEMY_ECHO = False
    pass

@tools.command()
def count():
    with app.app_context():
        c = get_counts()
        click.echo(c)
    return

@tools.command()
def xday():
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
    creds = Creds(app)
    with app.app_context():
        output = update_chart(creds, app)
        click.echo('db updated')
    return output

@tools.command()
@click.option("-a", "--artist")
@click.option("-g", "--gender")
def gender(artist, gender):
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
    
        
