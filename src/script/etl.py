import os
import glob
import psycopg2
import pandas as pd
from sql_queries import *
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())
lc_host = os.getenv('local_host')
db_port = os.getenv('local_db_port')
db_user = os.getenv('local_db_name')
db_name = os.getenv('local_db_name')
db_password = os.getenv('local_db_password')


def process_song_file(cur, filepath):
    """
    function proceess song files
    :param cur: instance of DB connection
    :param filepath: path to a single song file
    update Database with extracted content
    """
    # open song file
    df = pd.read_json(filepath, lines=True)
    df['duration'] = round(df['duration'])

    # insert song record
    song_data = df[['song_id', 'title', 'artist_id', 'year', 'duration']]
    song_data = tuple(song_data.values[0])
    cur.execute(song_table_insert, song_data)

    # insert artist record
    artist_data = df[['artist_id', 'artist_name', 'artist_location', 'artist_latitude', 'artist_longitude']]
    artist_data = tuple(artist_data.values[0])
    cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    """
    function proceess song files
    :param cur: instance of DB connection
    :param filepath: path to a single log files
    update Database with extracted content
    """
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df[df['page'] == 'NextSong']

    # convert timestamp column to datetime
    t = pd.to_datetime(df['ts'], unit='ms')
    # print('head: ',t.head(1),'\n')
    # insert time data records
    time_data = [
        (round(x.timestamp()),
         x.hour,
         x.day,
         x.week,
         x.month,
         x.year,
         x.weekday())
        for x in t
    ]
    # print('time_data',time_data,'\n')
    column_labels = ('timestamp',
                     'hour',
                     'day',
                     'week',
                     'month',
                     'year',
                     'weekday')
    time_df = pd.DataFrame(time_data, columns=column_labels)

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = df[['userId', 'firstName', 'lastName', 'gender', 'level']]

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for index, row in df.iterrows():

        # get songid and artistid from song and artist tables
        cur.execute(song_select, ((row.song, row.artist, round(row.length))))
        results = cur.fetchone()

        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None
            continue
        print(songid, artistid)

        # insert songplay record
        songplay_data = (round(row.ts / 1000.0), row.userId, row.level, \
                         songid, artistid, row.sessionId, row.location, \
                         row.userAgent)
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    """
    a global function to process log/song files
    :param cur: cursor
    :param conn: connection to DB
    :param filepath: path to the top directory
    """
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root, '*.json'))
        for f in files:
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():

    conn = psycopg2.connect(host=lc_host,
                            database='sparkifydb',
                            port=db_port,
                            user=db_user,
                            password=db_password)
    cur = conn.cursor()

    process_data(cur, conn, filepath='../../data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='../../data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()