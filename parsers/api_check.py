# -*- coding: utf-8 -*-
#!/usr/bin/python
"""
"""
import requests
import time
import os
from dotenv import load_dotenv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
key = os.getenv("WORDNIK_API_KEY")

def does_example_exist(word):
    query_string = {"api_key": key, "useCanonical": False}
    res = requests.get(
            "https://api.wordnik.com/v4/word.json/{}/topExample?".format(word),
        params=query_string,
        verify=False,
    )

    if res.status_code in set([429, 529, 504]):
        print("Wordnik API RATELIMIT. Response: {}".format(res.text))
        time.sleep(70)
        return does_example_exist(word)

    if res.status_code == 500:
        print("Wordnik API 500")
        return False

    result = res.json()
    # print("Wordnik response: {}".format(res.text))

    if result.get("statusCode") == 404:
        print("No examples in Wordnik API search response: {}".format(res.text))
        return False

    return True
