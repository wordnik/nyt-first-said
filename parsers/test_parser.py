#!/usr/bin/python
"""
Test a parser.  For example:

$ python test_parser.py nyt.NYTParser
[list of URLs to check]
$ python test_parser.py nyt.NYTParser <one of those URLs>
[text of article to store]
"""

import sys
from nyt import NYTParser

try:
    parsername = sys.argv[1]
except IndexError:
    print 'Usage: test_parser.py <modulename>.<classname> [<url_to_check>]'
    sys.exit()

try:
    url = sys.argv[2]
except IndexError:
    url = None

parser = NYTParser

if url:
    parsed_article = parser(url)
    print unicode(parsed_article.body)
else:
    links = parser.feed_urls()
    print '\n'.join(links)
