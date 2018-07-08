from urllib.request import urlretrieve
from bs4 import BeautifulSoup


def dict_factory(cursor, row):
    return {col[0] : row[idx]
            for idx, col in enumerate(cursor.description)}


class LazySoup(object):
    
    def __init__(self, url):
        self.url = url
        
    def __call__(self):
        if not hasattr(self, 'soup'):
            # use urlretrieve instead of urlopen to enable caching
            fname, _ = urlretrieve(self.url)
            with open(fname, 'rb') as page:
                self.soup = BeautifulSoup(page, 'html.parser')
        return self.soup
    