# -*- coding: utf-8 -*-
#!/usr/bin/python
"""
"""
import requests
import time
from raven import Client

client = Client(
'https://aee9ceb609b549fe8a85339e69c74150:8604fd36d8b04fbd9a70a81bdada5cdf@sentry.io/1223891')



key = "f02981de7e824038967f4194b7815c8d"



def check_api(word):
    query_string = { 'api-key': key, 'q': '"%s"' % word}
    req = requests.get('https://api.nytimes.com/svc/search/v2/articlesearch.json', params=query_string, verify=False)
    
    if req.status_code in set([429, 529, 504]):
        time.sleep(50)
        client.captureMessage("NYT API RATELIMIT")
        return check_api(word)
    
    if req.status_code == 500:
        client.captureMessage("NYT API 500", extra={
            'req':req,
            'word': word,
        })
        return False 

    result = req.json()
    num_results = len(result['response']['docs'])
    return num_results
