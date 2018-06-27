from sqlite3 import dbapi2 as sqlite3
from contextlib import closing
import os
from utils import dict_factory
from db import visited_pages_table, import_sources_table
import db


def filter_pages(db_conn, pages):
    with closing(db_conn.cursor()) as c:
        c.execute(f'SELECT url FROM {visited_pages_table}')
        visited_urls = set(row['url'] for row in c.fetchall())
    pages = [row for row in pages 
             if row['url'] not in visited_urls]
    pages = [row for row in pages
             if row['url'] and row['title']]
    return pages


def firefox(db_conn, firefox_profile_path):
    places_sqlite_path = os.path.join(firefox_profile_path, 'places.sqlite')
    with sqlite3.connect(places_sqlite_path) as ff_conn:
        ff_conn.row_factory = dict_factory
        db.ensure_tables_exist(db_conn)
        with closing(ff_conn.cursor()) as c_inp, \
                closing(db_conn.cursor()) as c_out:
            # import pages
            c_inp.execute('SELECT url, title FROM moz_places')
            places = filter_pages(db_conn, c_inp.fetchall())
            c_out.executemany(f"""
                    INSERT INTO {visited_pages_table} ('url', 'title')
                    VALUES (?, ?)""", 
                    [(row['url'], row['title']) for row in places])
            # record the source
            c_out.execute(f"SELECT * FROM {import_sources_table}  "
                          "WHERE type='firefox' and path = ?", 
                          [firefox_profile_path])
            if not c_out.fetchall():
                c_out.execute("INSERT INTO import_sources ('path', 'type') "
                              "VALUES (?, 'firefox')", 
                              [firefox_profile_path])
    db_conn.commit()
    return len(places)
            