# -*- coding: utf-8 -*-
#!/usr/bin/python
"""
"""
import requests
import time

key = ""
def check_api(word):
    query_string = { 'api-key': key, 'q': word}
    req = requests.get('https://api.nytimes.com/svc/search/v2/articlesearch.json', params=query_string)
    if req.status_code in set([429, 529, 504]):
        time.sleep(25)
        return check_api(word)
    result = req.json()
    if req.status_code == 500:
        return False 
    numResults = len(result['response']['docs'])
    return numResults < 2
