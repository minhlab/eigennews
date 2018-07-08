'''
Created on 7 Jul 2018

@author: cumeo
'''

from db import monitored_pages_table, article_sources_table
from db import connect_db
from contextlib import closing
from urllib.request import urlretrieve, urlopen
from multiprocessing.dummy import Pool as ThreadPool
from collections import namedtuple
from time import time
from urllib.error import URLError, HTTPError
import sys
from tqdm import tqdm
from difflib import SequenceMatcher
from bs4 import BeautifulSoup


NewMonitoredPage = namedtuple("ArticleSource", ['url', 'html_content', 'timestamp'])


def query_html_source(url):
    try:
        fname, _ = urlretrieve(url)
        with open(fname, 'rb') as page:
            html_content = page.read()
        return NewMonitoredPage(url, html_content, time())
    except (URLError, HTTPError):
        print(f'Error retrieving {url}', file=sys.stderr)
        return None
        

def import_html_sources(conn, c):
    c.execute(f"SELECT url FROM {article_sources_table} WHERE type='html'")
    source_urls = set(d['url'] for d in c.fetchall())
    c.execute(f'SELECT url FROM {monitored_pages_table}')
    monitored_urls = set(d['url'] for d in c.fetchall())
    new_urls = source_urls.difference(monitored_urls)
    
    with ThreadPool(16) as thread_pool:  # use it instead of processes to be lightweight 
        new_monitored_pages = thread_pool.imap_unordered(query_html_source, new_urls)
        new_monitored_pages = tqdm(new_monitored_pages, total=len(new_urls),
                                   unit='URL', desc='Importing new pages')
        new_monitored_pages = [p for p in new_monitored_pages if p]
        c.executemany(f'''
            INSERT OR IGNORE INTO {monitored_pages_table} 
            (url, html_content, timestamp)
            VALUES (?, ?, ?)
            ''', new_monitored_pages)
        conn.commit()
        

def import_sources():
    with connect_db() as conn, closing(conn.cursor()) as c:
        import_html_sources(conn, c)
        

NewURLsInfo = namedtuple("NewURLsInfo", ["hrefs", "src_url", "html_content", "timestamp"])


def find_new_urls(url, recorded_html_content):
    timestamp = time()
    with urlopen(url) as page:
        html_content = page.read()
    s = SequenceMatcher(lambda _: 0, recorded_html_content, html_content)
    added_chunks = [html_content[j1:j2]
                    for tag, i1, i2, j1, j2 in s.get_opcodes()
                    if tag == 'insert']
    hrefs = [href for chunk in added_chunks 
             for a in BeautifulSoup(chunk, 'html.parser').findAll('a')
             for href in a.attrs['href'] if 'href' in a.attrs] 
    return NewURLsInfo(hrefs, url, html_content, timestamp)
    
    
def fetch_new_articles_from_html_sources(conn, c):
    c.execute(f'''
        SELECT url, html_content, update_freqency 
        FROM {monitored_pages_table}
        WHERE id in (SELECT id FROM {monitored_pages_table} 
                     WHERE next_update < {time():.0f}
                     ORDER BY RANDOM() LIMIT 1000)
        ''')
    monitored_pages = c.fetchall()
    # TODO: threading 
    info = [find_new_urls(p['url'], p['html_content']) for p in monitored_pages]
    info = [i for i in info if i.hrefs]
    href_lists, urls, html_contents, timpestamps = zip(*info)
    # TODO: calculate update frequency
    hrefs = set(href for hrefs in href_lists for href in hrefs)
    c.executemany(f'''
        UPDATE {monitored_pages_table} 
        SET html_content = ?,
            timestamp = ?,
        WHERE url = ?''', 
            zip(html_contents, timpestamps, urls))
    
    
def fetch_new_articles():
    with connect_db() as conn, closing(conn.cursor()) as c:
        fetch_new_articles_from_html_sources(conn, c)
    # import new sources for the next call
    import_sources()