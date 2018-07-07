'''
Extracting content from news articles
'''

import re
from newspaper import Article
from newspaper.article import ArticleException

with open('data/newspapers.txt') as f:
    news_domains = f.readlines()

news_domains_regex = '|'.join(re.escape(d.strip()) for d in news_domains)
news_url_regex = re.compile(f'https?://(?:www\.)?(?:{news_domains_regex})/') 


def newspaper3k(url, _):
    ''' Using newspaper3k to try parsing the page '''
    if news_url_regex.match(url):
        try:
            article = Article(url)
            article.download()
            article.parse()
            article.nlp()
            return {'url': url,
                    'authors': article.authors,
                    'content': article.text,
                    'publish_date': article.publish_date,
                    'top_image': article.top_image,
                    'movies': article.movies,
                    'keywords': article.keywords,
                    'summary': article.summary}
        except ArticleException: 
            return None