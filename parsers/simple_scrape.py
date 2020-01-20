# -*- coding: utf-8 -*-
#!/usr/bin/python

import sys
import redis
import string
import regex as re
import time
import raven
import twitter
import langid
from twitter_creds import TwitterApi, TwitterApiContext
from api_check import check_api
from nyt import NYTParser

reload(sys)
sys.setdefaultencoding('utf8')

from raven import Client

client = Client(
'https://aee9ceb609b549fe8a85339e69c74150:8604fd36d8b04fbd9a70a81bdada5cdf@sentry.io/1223891')
api = TwitterApi()
contextApi = TwitterApiContext()

r = redis.StrictRedis(host='localhost', port=6379, db=0)


parser = NYTParser


def humanize_url(article):
    return article.split('/')[-1].split('.html')[0].replace('-', ' ')


def check_word(word, article_url, word_context):
    time.sleep(1)
    print(word)
    if not check_api(word):
        client.captureMessage("API Rejection", extra={
            'word': word,
            'word_context': word_context,
        })
        return

    language, confidence = langid.classify(word_context)

    if language != 'en':
        client.captureMessage("Language Rejection", extra={
            'word': word,
            'word_context': word_context,
            'confidence': confidence
        })
        return

    if int(r.get("recently") or 0) < 8:
        r.incr("recently")
        r.expire("recently", 60 * 30)
        tweet_word(word, article_url, word_context)


def tweet_word(word, article_url, word_context):
    try:
        status = api.PostUpdate(word)
        contextApi.PostUpdate(
            "@{} \"{}\" occurred in: {}".format(
                status.user.screen_name,
                word_context,
                article_url),
            in_reply_to_status_id=status.id,
            verify_status_length=False)
    except UnicodeDecodeError:
        client.captureException()
    except twitter.TwitterError:
        client.captureException()


def ok_word(s):
    if s.endswith('.') or s.endswith('’'):  # trim trailing .
        s = s[:-1]

    if not s.islower():
        return False

    return (not any(i.isdigit() or i in '.@/#-_' for i in s))


def remove_punctuation(text):
    return re.sub(ur"’s", "", re.sub(ur"\p{P}+$", "", re.sub(ur"^\p{P}+", "", text)))


def normalize_punc(raw_word):
    replaced_chars = [',', '—', '”', '“', ':', '\'', '’s', '"', u'\u200B', u'\u200E']
    for char in replaced_chars:
        raw_word = raw_word.replace(char, ' ')

    raw_word = raw_word.replace(u"\u00AD", '-')

    return raw_word.split(' ')


def context(content, word):
    loc = content.find(word)
    to_period = content[loc:].find('.')
    prev_period = content[:loc].rfind('.')
    allowance = 82
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
                    check_word(word, article, context(text, word))
                    r.set(wkey, '1')


def process_links(links):
    for link in links:
        akey = "article:" + link
        seen = r.get(akey)
    	print(akey+" seen: " + str(seen))
#    	seen = False
        # unseen article
        if not seen:
            time.sleep(1)
            parsed_article = parser(link).body
            process_article(parsed_article, link)
            r.set(akey, '1')


start_time = time.time()

process_links(parser.feed_urls())
#process_links(['https://www.nytimes.com/2019/11/06/magazine/turtleneck-man-bbc-question-time-brexit.html'])



elapsed_time = time.time() - start_time
print('Time Elapsed (seconds):')
print(elapsed_time)


