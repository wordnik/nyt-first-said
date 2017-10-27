# -*- coding: utf-8 -*-
#!/usr/bin/python
"""
"""

import sys
import redis
import string
import regex as re
import time
import raven
import twitter
from twitter_creds import TwitterApi, TwitterApiContext
from api_check import check_api

reload(sys)  
sys.setdefaultencoding('utf8')

from raven import Client

client = Client('https://ad7b9867c209488da9baa4fbae04d8f0:b63c0acd29eb40269b52d3e6f82191d9@sentry.io/144998')

api = TwitterApi()
contextApi = TwitterApiContext()

r = redis.StrictRedis(host='localhost', port=6379, db=0)

parsername = "nyt.NYTParser"

try:
    url = sys.argv[1]
except IndexError:
    url = None

module, classname = parsername.rsplit('.', 1)
parser = getattr(__import__(module, globals(), fromlist=[classname]), classname)

def tweet_word(word):
    client.captureMessage("posted: "+word)
    time.sleep(1)    
    if not check_api(word):
        return
    if int( r.get("recently") or 0 ) < 3:
        r.incr("recently")
        r.expire("recently", 60 * 30)
        try:
            status = api.PostUpdate(word)
	    client.captureMessage(status,extra=status)
        except UnicodeDecodeError:
	    client.captureMessage(word)
	except twitter.TwitterError:
	    client.captureException()	
#        print("%s just posted: %s" % (status.user.name, status.text))

def ok_word(s):
    return (not any(i.isdigit() or i=='.' or i=='@' or i=='#' for i in s)) and s.islower() and s[0] is not '@'

def remove_punctuation(text):
    return re.sub(ur"’s","", re.sub(ur"\p{P}+$", "", re.sub(ur"^\p{P}+", "", text)))

def normalize_punc(raw_word):
    return raw_word.replace(',', '-').replace('—', '-').replace('/', '-').replace(':', '-').replace('\'', '-').replace('’','-').split('-')

def process_article(content):
    text = unicode(content)
    words = text.split()
    for raw_word_h in words:
        for raw_word in normalize_punc(raw_word_h):
            if ok_word(raw_word):
                word = remove_punctuation(raw_word)
                wkey = "word:" + word
                if not r.get(wkey):
                    tweet_word(word)
                    r.set(wkey, '1')

links = parser.feed_urls()
for link in links:
    akey = "article:"+link
    if not r.get(akey):
	time.sleep(1)
        parsed_article = parser(link)
        process_article(parsed_article)
        r.set(akey, '1')
