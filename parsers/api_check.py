# -*- coding: utf-8 -*-
#!/usr/bin/python
"""
"""
import requests
import time
import os
from sentry_sdk import capture_message


key = os.environ.get("NYT_API_KEY")


def check_api(word):
    query_string = {"api-key": key, "q": '"%s"' % word}
    req = requests.get(
        "https://api.nytimes.com/svc/search/v2/articlesearch.json",
        params=query_string,
        verify=False,
    )

    if req.status_code in set([429, 529, 504]):
        time.sleep(50)
        capture_message("NYT API RATELIMIT")
        return check_api(word)

    if req.status_code == 500:
        capture_message("NYT API 500")
        return False

    result = req.json()
    num_results = len(result["response"]["docs"])
    return num_results
