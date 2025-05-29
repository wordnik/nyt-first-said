#!/usr/bin/python
"""
Try a parser.  For example:

$ python try_parser.py nyt.NYTParser
[list of URLs to check]
$ python try_parser.py nyt.NYTParser <one of those URLs>
[text of article to store]
"""

import sys
from parsers.nyt import NYTParser

try:
    url = sys.argv[1]
except IndexError:
    print('Usage: try_parser.py  [<url_to_check>]')
    sys.exit()

parser = NYTParser

if url:
    parsed_article = parser(url)
    print(parsed_article.body)
else:
    links = parser.feed_urls()
    print('\n'.join(links))
