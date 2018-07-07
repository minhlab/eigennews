from scrape.qa import scrape_stackoverflow_question
from db import connect_db
from db import visited_pages_table
from urllib.error import URLError
import sys
from contextlib import closing
from tqdm import tqdm
from multiprocessing.dummy import Pool as ThreadPool
from scrape.news import newspaper3k
import re
from utils import LazySoup



with open('data/ignore.txt') as f:
    ignore_domains = f.readlines()

ignore_domains_regex = '|'.join(re.escape(d.strip()) for d in ignore_domains)
ignore_url_regex = re.compile(f'https?://(?:www\.)?(?:{ignore_domains_regex})/') 


def ignore(url, _):
    if ignore_url_regex.match(url):
        return {'url': url, 'ignored': 1}


_scraping_funcs = [
    scrape_stackoverflow_question,
    newspaper3k,
    ignore,
]


def extract_docs(url):
    try:
        soup_func = LazySoup(url)
        docs_iter = (func(url, soup_func) for func in _scraping_funcs)
        docs_iter = (docs for docs in docs_iter if docs is not None)
        return next(docs_iter, None)
    except URLError:
        print(f'Error retrieving {url}', file=sys.stderr)
        return None
    

def scrape_all_visited_page():
    with connect_db() as conn, closing(conn.cursor()) as c:
        c.execute(f'SELECT url from {visited_pages_table} WHERE scraped = 0')
        urls = [row['url'] for row in c.fetchall()]
        with ThreadPool(16) as thread_pool:  # use it instead of processes to be lightweight 
            # use iters from here on to avoid keeping too many documents in memory
            docs = thread_pool.imap_unordered(extract_docs, urls)
            docs = tqdm(docs, unit='URL', desc='Scraping', total=len(urls))
            docs = (doc for doc in docs if doc)
            # only set scrape=1 for URLs that were successfully interpreted
            # so that when we have a new way to scrape content, we can 
            # retrospectively process old URLs
            c.executemany(f'''
                UPDATE {visited_pages_table} 
                SET content = ?, 
                    publish_date = ?, 
                    top_image = ?,
                    visit_date = ?,
                    summary = ?,
                    keywords = ?,
                    ignored = ?,
                    scraped = 1
                WHERE url = ?''', 
                          ((doc.get('content', '').encode('utf-8'),
                            doc.get('publish_date'),
                            doc.get('top_image'),
                            doc.get('visit_date'),
                            doc.get('summary'),
                            doc.get('ignored', 0),
                            ','.join(doc.get('keywords', [])),
                            doc['url'])
                           for doc in docs))
        conn.commit()
