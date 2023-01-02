# db init
from pymysql import connect
from pymysql import err
import os

if os.environ.get('LOCAL') == "True":
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

def db_commit(q, conn=mysql_conn):
    with conn.cursor() as cur:
        cur.execute(q)
        conn.commit()
        return

def db_query(q, conn=mysql_conn):
    with conn.cursor() as cur:
        cur.execute(q)
    return cur.fetchall()
