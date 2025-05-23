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
    res = requests.get(
        "https://api.nytimes.com/svc/search/v2/articlesearch.json",
        params=query_string,
        verify=False,
    )

    if res.status_code in set([429, 529, 504]):
        print("NYT API RATELIMIT. Response: {}".format(res.text))
        time.sleep(70)
        return check_api(word)

    if res.status_code == 500:
        print("NYT API 500")
        return False

    result = res.json()
    num_results = 0

    docs = result.get("response", {}).get("docs", [])
    # Sometimes `docs` is null.
    if docs:
        num_results = len(docs)

    if num_results < 1:
        print("No docs in NYT API search response: {}".format(res.text))

    return num_results
