# -*- coding: utf-8 -*-
#!/usr/bin/python
"""
"""
import requests

key = ""
def check_api(word):
    query_string = { 'api-key': key, 'q': word}
    req = requests.get('https://api.nytimes.com/svc/search/v2/articlesearch.json', params=query_string)
    result = req.json()
    numResults = len(result['response']['docs'])
    return numResults < 3