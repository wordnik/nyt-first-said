# -*- coding: utf-8 -*-
#!/usr/bin/python
"""
"""
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("NYT_API_KEY")

def check_api(word):
    query_string = {"api-key": key, "q": '"%s"' % word}
    req = requests.get(
        "https://api.nytimes.com/svc/search/v2/articlesearch.json",
        params=query_string,
        verify=False,
    )

    if req.status_code in set([429, 529, 504]):
        time.sleep(50)
        print("NYT API RATELIMIT")
        return check_api(word)

    if req.status_code == 500:
        print("NYT API 500")
        return False

    result = req.json()
    num_results = 0

    docs = result.get("response", {}).get("docs", [])
    # Sometimes `docs` is null.
    if docs:
        num_results = len(docs)

    if num_results < 1:
        print("No docs in NYT API search response: {}".format(req.text))

    return num_results
