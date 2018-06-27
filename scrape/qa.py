'''
Scraping question answering websites such as Stackoverflow and Quora
'''

import re

with open('data/stackoverflow.txt') as f:
    stackoverflow_domains = f.readlines()

stackoverflow_domains_regex = '|'.join(re.escape(d.strip()) for d in stackoverflow_domains)
stackoverflow_question_regex = re.compile(f'https?://(?:www\.)?(?:{stackoverflow_domains_regex})/questions/') 
                                         

def scrape_stackoverflow_question(url, soup_func):
    if stackoverflow_question_regex.match(url):
        soup = soup_func()
        title = soup.find('a', attrs= {'class': 'question-hyperlink'})
        posts = soup.findAll('div', attrs= {'class': 'post-text'})
        return {'url': url,
                'title': title.text.strip(),
                'content': '\n\n'.join(post.text.strip() for post in posts)}