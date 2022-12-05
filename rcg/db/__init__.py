# db init
from pymysql import connect
import os

if os.environ['FLASK_ENV'] == "development":
    mysql_conn = connect(
        user=os.environ['LOCAL_MYSQL_USER'],
        password=os.environ['LOCAL_MYSQL_PW'],
        host=os.environ['LOCAL_MYSQL_URL'],
        port=3306,
        db='rcg-testo'
    )

else:
    mysql_conn = connect(
        user=os.environ['MYSQL_USER'],
        password=os.environ['MYSQL_PW'],
        host=os.environ['MYSQL_URL'],
        port=3306,
        db='rcg'
    )

def db_commit(q, conn=mysql_conn):
    with conn.cursor() as cur:
        cur.execute(q)
    conn.commit()
    return

def db_query(q, conn=mysql_conn):
    with conn.cursor() as cur:
        cur.execute(q)
    return cur.fetchall()
