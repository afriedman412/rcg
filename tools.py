from rcg import app_, db_
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

if __name__=="__main__":
    load_dotenv()
    tools()
