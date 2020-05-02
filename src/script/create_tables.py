import os
import psycopg2
from dotenv import load_dotenv, find_dotenv
from sql_queries import create_table_queries, drop_table_queries

load_dotenv(find_dotenv())
lc_host = os.getenv('local_host')
db_port = os.getenv('local_db_port')
db_user = os.getenv('local_db_name')
db_name = os.getenv('local_db_name')
db_password = os.getenv('local_db_password')


def create_database():
    """
    - Creates and connects to the sparkifydb
    - Returns the connection and cursor to sparkifydb
    """

    # connect to default database
    conn = psycopg2.connect(host=lc_host,
                            database=db_name,
                            port=db_port,
                            user=db_user,
                            password=db_password)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    # create sparkify database with UTF8 encoding
    cur.execute("DROP DATABASE IF EXISTS sparkifydb")
    cur.execute("CREATE DATABASE sparkifydb WITH ENCODING 'utf8' TEMPLATE template0")

    # close connection to default database
    conn.close()

    # connect to sparkify database
    conn = psycopg2.connect(host=lc_host,
                            database='sparkifydb',
                            port=db_port,
                            user=db_user,
                            password=db_password)
    cur = conn.cursor()

    return cur, conn


def drop_tables(cur, conn):
    """
    Drops each table using the queries in `drop_table_queries` list.
    """
    for query in drop_table_queries:
        print('drop_tables: ', query)
        cur.execute(query)
        conn.commit()


def create_tables(cur, conn):
    """
    Creates each table using the queries in `create_table_queries` list.
    """
    for query in create_table_queries:
        print('create_tables:', query)
        cur.execute(query)
        conn.commit()


def main():
    """
    - Drops (if exists) and Creates the sparkify database.

    - Establishes connection with the sparkify database and gets
    cursor to it.

    - Drops all the tables.

    - Creates all tables needed.

    - Finally, closes the connection.
    """
    cur, conn = create_database()

    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()