# -*- coding: utf-8 -*-
#!/usr/bin/python

import sys
import redis
import string
import regex as re
import time
import raven
import twitter
from twitter_creds import TwitterApi, TwitterApiContext
from api_check import check_api
from nyt import NYTParser

reload(sys)
sys.setdefaultencoding('utf8')

from raven import Client

client = Client(
    'https://ad7b9867c209488da9baa4fbae04d8f0:b63c0acd29eb40269b52d3e6f82191d9@sentry.io/144998')

api = TwitterApi()
contextApi = TwitterApiContext()

r = redis.StrictRedis(host='localhost', port=6379, db=0)


parser = NYTParser

def humanize_url(article):
    return article.split('/')[-1].split('.html')[0].replace('-', ' ')


def check_word(word, article_url, article_content):
    time.sleep(1)
    if not check_api(word):
        return
    if int(r.get("recently") or 0) < 4:
        r.incr("recently")
        r.expire("recently", 60 * 30)
        tweet_word(word, article_url, article_content)


def tweet_word(word, article_url, article_content):
    try:
        status = api.PostUpdate(word)
        contextApi.PostUpdate(
            "@{} \"{}\" occurred in: {}".format(
                status.user.screen_name,
                context(article_content, word),
                article_url),
            in_reply_to_status_id=status.id,
            verify_status_length=False)
    except UnicodeDecodeError:
        client.captureException()
    except twitter.TwitterError:
        client.captureException()


def ok_word(s):
    if s.endswith('.'):  # trim trailing .
        s = s[:-1]
    return (not any(i.isdigit() or i == '.' or i == '@' or i == '/' or i == '#' for i in s)) and s.islower() and s[0] is not '@'


def remove_punctuation(text):
    return re.sub(ur"’s", "", re.sub(ur"\p{P}+$", "", re.sub(ur"^\p{P}+", "", text)))


def normalize_punc(raw_word):
    replaced_chars = [',', '—', '”', ':', '\'', '’', '"']
    for char in replaced_chars:
        raw_word = raw_word.replace(char,'-')

    return raw_word.split('-')


def context(content, word):
    loc = content.find(word)
    to_period = content[loc:].find('.')
    prev_period = content[:loc].rfind('.')
    allowance = 45
    if to_period < allowance:
        end = content[loc:loc + to_period + 1]
    else:
        end = u'{}…'.format(content[loc:loc + allowance])

    if loc - prev_period < allowance:
        start = u'{} '.format(content[prev_period + 2: loc].strip())
    else:
        start = u'…{}'.format(content[loc - allowance:loc])

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
                    check_word(word, article, text)
                    r.set(wkey, '1')


def process_links(links):
    for link in links:
        akey = "article:" + link
        
        # unseen article
        if not r.get(akey): 
            time.sleep(1)
            parsed_article = parser(link)
            process_article(parsed_article, link)
            r.set(akey, '1')

process_links(parser.feed_urls())