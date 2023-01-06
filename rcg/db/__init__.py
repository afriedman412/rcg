# db init
from pymysql import connect
import os

def make_sql_connection(local: bool=False):
    if local:
        print('*** USING LOCAL DB ***')
        mysql_conn = connect(
            user=os.environ.get('LOCAL_MYSQL_USER'),
            password=os.environ.get('LOCAL_MYSQL_PW'),
            host=os.environ.get('LOCAL_MYSQL_URL'),
            port=3306,
            db='rcg-testo'
        )

    else:
        print('*** USING REMOTE DB ***')
        mysql_conn = connect(
            user=os.environ.get('MYSQL_USER'),
            password=os.environ.get('MYSQL_PW'),
            host=os.environ.get('MYSQL_URL'),
            port=3306,
            db='rcg'
        )
    
    return mysql_conn

if os.environ.get("LOCAL"):
    conn = make_sql_connection(True)
else:
    conn = make_sql_connection()

def db_commit(q, conn=conn):
    with conn.cursor() as cur:
        cur.execute(q)
        conn.commit()
        return

def db_query(q, conn=conn):
    with conn.cursor() as cur:
        cur.execute(q)
    return cur.fetchall()
