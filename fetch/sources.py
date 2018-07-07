'''
Created on 5 Jul 2018

@author: Minh Le
'''

from db import connect_db
from db import visited_pages_table, article_sources_table
from contextlib import closing
from multiprocessing.dummy import Pool as ThreadPool
from tqdm import tqdm
from urllib.parse import urlparse
from urllib.parse import urljoin
import re
from utils import LazySoup
from urllib.error import URLError
import sys
from itertools import chain
from collections import namedtuple


ArticleSource = namedtuple("ArticleSource", ['url', 'type', 'provenance'])


def _url_lengths(url):
    '''
    Return the length of an URL according to a few heuristics that aim at
    capturing the "listing-ness" of a page (the shorter an URL, the more likely
    it is a listing page). 
    '''
    o = urlparse(url)
    path_len = o.path.count('/')
    word_len = len(re.findall(r'[\w\d]+', url))
    char_len = len(url)
    return (path_len, word_len, char_len)
    

def length_based_extractor(url, soup_func):
    '''
    This method assumes that shorter URLs lead to listing pages (think homepage,
    topics, categories, tags, author page) so it will return the 10 shortest 
    URLs that are linked to in a given page.
    '''
    o = urlparse(url)
    domain = f"{o.scheme}://{o.netloc}/"
    soup = soup_func()
    hrefs = [urljoin(url, a.attrs['href']) 
             for a in soup.findAll('a') if 'href' in a.attrs]
    hrefs = [href for href in hrefs if href.startswith(domain)]
    hrefs = set(hrefs)
    hrefs = sorted(hrefs, key=_url_lengths)
    provenance = f'discovered in {url} by length_based_extractor()'
    return [ArticleSource(url=href, type='html', provenance=provenance)
            for href in hrefs[:10]]


_extract_funcs = [
    length_based_extractor
]
    
    
def extract_sources(url):
    try:
        soup_func = LazySoup(url)
        srcs_iter = (func(url, soup_func) for func in _extract_funcs)
        return next(srcs_iter, None)
    except URLError:
        print(f'Error retrieving {url}', file=sys.stderr)
        return None
    

def search_all_scraped_pages_for_sources():
    with connect_db() as conn, closing(conn.cursor()) as c:
        # somehow content != '' still returns articles with empty content so
        # I use length instead 
        c.execute(f'''
            SELECT url from {visited_pages_table} 
            WHERE length(ifnull(content, '')) > 0 AND source_searched = 0''')
        urls = [row['url'] for row in c.fetchall()]
        with ThreadPool(16) as thread_pool:  # use it instead of processes to be lightweight 
            # use iters from here on to avoid keeping too many documents in memory
            srcs = thread_pool.imap_unordered(extract_sources, urls)
            srcs = tqdm(srcs, unit='URL', desc='Searching', total=len(urls))
            srcs = (src for src in srcs if src)
            srcs = chain.from_iterable(srcs)
            c.executemany(f'''
                INSERT OR IGNORE INTO {article_sources_table} 
                (url, type, provenance)
                VALUES (?, ?, ?)
                ''', srcs)
        c.executemany(f'''
            UPDATE {visited_pages_table} 
            SET source_searched = 1
            WHERE url = ?''', [(url,) for url in urls])
        conn.commit()
