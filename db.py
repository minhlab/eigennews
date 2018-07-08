from contextlib import closing
import config
from sqlite3 import dbapi2 as sqlite3
from utils import dict_factory

# see https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers
_url_length = 8000

visited_pages_table = 'visited_pages'
import_sources_table = 'import_sources'
article_sources_table = 'article_sources'
monitored_pages_table = 'monitored_pages'

__create_import_source_table_cmd = f'''
    CREATE TABLE IF NOT EXISTS {import_sources_table} (
        id INTEGER PRIMARY KEY,
        name varchar(100) DEFAULT NULL,
        type varchar(100) DEFAULT NULL,
        path varchar(1000) NOT NULL
    )
'''

# provenance column is for troubleshooting
__create_article_source_table_cmd = f'''
    CREATE TABLE IF NOT EXISTS {article_sources_table} (
        id INTEGER PRIMARY KEY,
        type varchar(100) DEFAULT NULL,
        url varchar({_url_length}) NOT NULL UNIQUE,
        provenance varchar(1000) NOT NULL,
        preference_score REAL DEFAULT 0
    )
'''

__create_visited_pages_table_cmd = f'''
    CREATE TABLE IF NOT EXISTS {visited_pages_table} (
        id INTEGER PRIMARY KEY, 
        url varchar({_url_length}) NOT NULL, 
        title varchar(1000) NOT NULL, 
        content BLOB DEFAULT NULL,
        scraped INTEGER(1) DEFAULT 0,
        source_searched INTEGER(1) DEFAULT 0,
        ignored INTEGER(1) DEFAULT 0,
        publish_date varchar(50) DEFAULT NULL,
        top_image varchar(1000) DEFAULT NULL,
        visit_date varchar(50) DEFAULT NULL,
        summary varchar(2000) DEFAULT NULL,
        keywords varchar(2000) DEFAULT NULL
    )
'''

__create_monitored_pages_table_cmd = f'''
    CREATE TABLE IF NOT EXISTS {monitored_pages_table} (
        id INTEGER PRIMARY KEY, 
        url varchar({_url_length}) NOT NULL UNIQUE, 
        html_content BLOB DEFAULT NULL,
        timestamp INTEGER,
        update_freqency INTEGER DEFAULT 0,
        next_update INTEGER DEFAULT 0
    )
'''


def ensure_tables_exist(db_conn):
    with closing(db_conn.cursor()) as c:
        c.execute(__create_import_source_table_cmd)
        c.execute(__create_visited_pages_table_cmd)
        c.execute(__create_article_source_table_cmd)
        c.execute(__create_monitored_pages_table_cmd)
    db_conn.commit()
    

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(config.DATABASE)
    rv.row_factory = dict_factory
    ensure_tables_exist(rv)
    return rv
