"""Access point to all functionalities of the project.

Usage:
  main.py serve
  main.py import --browser=<brwsr> --profile=<path>
  main.py scrape
  main.py search_sources
  main.py fetch
  
Options:
  -h --help          Show this screen.
  --browser=<brwsr>  Type of browser (only "firefox" is supported so far)
  --profile=<path>   Path to the profile folder 
  
"""
from docopt import docopt
import sys

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Samantha 0.0.1')
    if arguments['serve']:
        from flaskr import app
        app.run()
    elif arguments['import']:
        from db import connect_db
        from integration import imports
        browser = arguments['--browser']
        if browser == 'firefox':
            imported_count = imports.firefox(connect_db(), arguments['--profile'])
        else:
            print(f"Unsupported browser: {browser}", file=sys.stderr)
            sys.exit(1)
        print(f'Imported {imported_count} pages.')
    elif arguments['scrape']:
        from scrape.scrape import scrape_all_visited_page
        scrape_all_visited_page()
    elif arguments['search_sources']:
        from fetch.sources import search_all_scraped_pages_for_sources
        search_all_scraped_pages_for_sources()
    elif arguments['fetch']:
        from fetch.fetchers import fetch_new_articles
        fetch_new_articles()
    else:
        print("Unsupported arguments: ", arguments)