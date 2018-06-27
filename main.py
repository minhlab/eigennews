"""Access point to all functionalities of the project.

Usage:
  main.py serve
  main.py scrape
  main.py import --browser=<brwsr> --profile=<path>
  
Options:
  -h --help          Show this screen.
  --browser=<brwsr>  Type of browser (only "firefox" is supported so far)
  --profile=<path>   Path to the profile folder 
  
"""
from docopt import docopt
import sys

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')
    if arguments['serve']:
        from flaskr import app
        app.run()
    elif arguments['scrape']:
        from scrape.scrape import scrape_all_visited_page
        scrape_all_visited_page()
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
    else:
        print("Unsupported arguments: ", arguments)