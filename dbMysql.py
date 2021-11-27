import pymysql

def get_conn():
    return  pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='bobpwd',
        #database='pysql',
        database='mulan',
        charset='utf8'
    )

def insert_or_update_data(sql):
    conn=get_conn()
    try:
        cursor=conn.cursor()
        cursor.execute(sql)
        conn.commit()
    finally:
        conn.close()


def query_data(sql):
    conn = get_conn()
    try:
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(sql)
        return cur.fetchall()
    finally:
        conn.close()

