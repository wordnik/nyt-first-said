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

client = Client(
    'https://ad7b9867c209488da9baa4fbae04d8f0:b63c0acd29eb40269b52d3e6f82191d9@sentry.io/144998')

api = TwitterApi()
contextApi = TwitterApiContext()

r = redis.StrictRedis(host='localhost', port=6379, db=0)

parsername = "nyt.NYTParser"

try:
    url = sys.argv[1]
except IndexError:
    url = None

module, classname = parsername.rsplit('.', 1)
parser = getattr(__import__(module, globals(),
                            fromlist=[classname]), classname)

def humanize_url(article):
    return article.split('/')[-1].split('.html')[0].replace('-', ' ')

def tweet_word(word, article_url, article_content):
    client.captureMessage("posted: " + word)
    time.sleep(1)
    if not check_api(word):
        return
    if int(r.get("recently") or 0) < 3:
        r.incr("recently")
        r.expire("recently", 60 * 30)
        try:
            status = api.PostUpdate(word)
            contextApi.PostUpdate(
                "@{} \"{}\" occurred in: {}".format(
	        status.user.screen_name,
	        context(article_content, word),
	        # humanize_url(article_url),
	        article_url),
                in_reply_to_status_id=status.id)
        except UnicodeDecodeError:
            client.captureException()
        except twitter.TwitterError:
            client.captureException()


def ok_word(s):
    if s.endswith('.'): #trim trailing .
        s = s[:-1]
    return (not any(i.isdigit() or i == '.' or i == '@' or i =='/' or i == '#' for i in s)) and s.islower() and s[0] is not '@'


def remove_punctuation(text):
    return re.sub(ur"’s", "", re.sub(ur"\p{P}+$", "", re.sub(ur"^\p{P}+", "", text)))


def normalize_punc(raw_word):
    return raw_word.replace(',', '-').replace('—', '-').replace('”','-').replace(':', '-').replace('\'', '-').replace('’', '-').split('-')


def context(content, word):
    loc = content.find(word)
    to_period = content[loc:].find('.')
    if to_period  < 40:
        end = content[loc:loc+to_period+1]
    else:
        end = u'{}…'.format(content[loc:loc+40])
    
    prev_period = content[:loc].rfind('.')
    if loc - prev_period  < 40:
        start = content[prev_period+2 : loc]
    else:
        start = u'…{}'.format(content[loc-40:loc])
    
    return u'{}{}'.format(start, end)


def process_article(content, article):
    text = unicode(content)
    words = text.split()
    for raw_word_h in words:
        for raw_word in normalize_punc(raw_word_h):
            if ok_word(raw_word):
                word = remove_punctuation(raw_word)
                wkey = "word:" + word
                if not r.get(wkey):
                    tweet_word(word, article, text)
                    r.set(wkey, '1')


links = parser.feed_urls()
for link in links:
    akey = "article:" + link
    if not r.get(akey):
        time.sleep(1)
        parsed_article = parser(link)
        process_article(parsed_article, link)
        r.set(akey, '1')
