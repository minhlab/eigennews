from urllib.request import urlopen
from bs4 import BeautifulSoup
from contextlib import closing


def dict_factory(cursor, row):
    return {col[0] : row[idx]
            for idx, col in enumerate(cursor.description)}


class LazySoup(object):
    
    def __init__(self, url):
        self.url = url
        
    def __call__(self):
        if not hasattr(self, 'soup'):
            with closing(urlopen(self.url)) as page:
                self.soup = BeautifulSoup(page, 'html.parser')
        return self.soup
    