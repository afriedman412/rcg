from rcg.db import db_commit, db_query
from rcg.code.helpers import get_date
from rcg.code.code import update_chart, Creds
import click
from dotenv import load_dotenv

@click.group()
# @click.option("-l", "--local", is_flag=True)
# @click.option("-s", "--silence", is_flag=True)
def tools():
    pass


@tools.command()
@click.option("-d", "--chart_date")
def day(chart_date=None):
    chart_date = chart_date if chart_date else get_date()
    q = f"""SELECT * FROM chart WHERE chart_date='{chart_date}'"""
    chart = db_query(q)
    for c in chart:
        print(c)
    return

@tools.command()
@click.option("-d", "--chart_date")
def xday(chart_date=None):
    chart_date = chart_date if chart_date else get_date()
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
    creds = Creds()
    output = update_chart(creds)
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
    load_dotenv()
    tools()
    
        
