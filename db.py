from contextlib import closing
import config
from sqlite3 import dbapi2 as sqlite3
from utils import dict_factory


visited_pages_table = 'visited_pages'
import_sources_table = 'import_sources'

__create_import_source_table_cmd = f'''
    CREATE TABLE IF NOT EXISTS {import_sources_table} (
        id INTEGER PRIMARY KEY,
        name varchar(100) DEFAULT NULL,
        type varchar(100) DEFAULT NULL,
        path varchar(1000) NOT NULL
    )
'''

__create_visited_pages_table_cmd = f'''
    CREATE TABLE IF NOT EXISTS {visited_pages_table} (
        id INTEGER PRIMARY KEY, 
        url varchar(256) NOT NULL, 
        title varchar(1000) NOT NULL, 
        content BLOB DEFAULT NULL,
        processed INTEGER(1) DEFAULT 0,
        ignored INTEGER(1) DEFAULT 0,
        publish_date varchar(50) DEFAULT NULL,
        top_image varchar(1000) DEFAULT NULL,
        visit_date varchar(50) DEFAULT NULL,
        summary varchar(2000) DEFAULT NULL,
        keywords varchar(2000) DEFAULT NULL
    )
'''


def ensure_tables_exist(db_conn):
    with closing(db_conn.cursor()) as c:
        c.execute(__create_import_source_table_cmd)
        c.execute(__create_visited_pages_table_cmd)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(config.DATABASE)
    rv.row_factory = dict_factory
    return rv
