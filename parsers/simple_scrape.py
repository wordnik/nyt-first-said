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
from datetime import date
today = date.today()

reload(sys)
sys.setdefaultencoding('utf8')

from raven import Client

client = Client(
'https://aee9ceb609b549fe8a85339e69c74150:8604fd36d8b04fbd9a70a81bdada5cdf@sentry.io/1223891')
api = TwitterApi()
contextApi = TwitterApiContext()

r = redis.StrictRedis(host='localhost', port=6379, db=0)


parser = NYTParser

date = today.strftime("%B-%d-%Y")

record = open("/home/max/newsdiffs/records/"+date+".txt", "a+") 

def humanize_url(article):
    return article.split('/')[-1].split('.html')[0].replace('-', ' ')


def check_word(word, article_url, word_context):
    time.sleep(1)
    print(word)
    client.captureMessage("API Checking Word",extra={
        'word': word,
    })
    count = check_api(word)
    if count > 1:
        client.captureMessage("API Rejection", extra={
            'word': word,
            'word_context': word_context,
        })
        record.write("~" + "API") 
        return count

    language, confidence = langid.classify(word_context)

    if language != 'en':
        client.captureMessage("Language Rejection", extra={
            'word': word,
            'word_context': word_context,
            'confidence': confidence
        })
        record.write("~" + "LANG") 
        return count
        
    record.write("~" + "GOOD") 
    record.write("~" + word) 
    if int(r.get("recently") or 0) < 8:
        r.incr("recently")
        r.expire("recently", 60 * 30)
 
        tweet_word(word, article_url, word_context)
    else:
        client.captureMessage("Recency Rejection", extra={
            'word': word
        })
    return count 

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

    return (not any(i.isdigit() or i in '(.@/#-_[' for i in s))


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
    # record = open("records/"+article.replace("/", "_")+".txt", "w+") 
    record.write("\nARTICLE:" + article) 
    text = unicode(content)
    words = text.split()
#    print(words)
    client.captureMessage("Processing Article",extra={
        'article': article,
        'length': len(words),
    })
    for raw_word_h in words:
        for raw_word in normalize_punc(raw_word_h):
            if len(raw_word) < 2:
                continue
            record.write("\n" +raw_word) 
            record.write("~" + remove_punctuation(raw_word)) 
            if ok_word(raw_word):
                word = remove_punctuation(raw_word)
                record.write("~" + word) 
                wkey = "word:" + word
                cache_count = r.get(wkey)
                if not cache_count:
                    # not in cache
                    c = check_word(word, article, context(text, word))
                    r.set(wkey, c)
                else: 
                    # seen in cache
                    record.write("~" + "C") 


def process_links(links):
    for link in links:
        akey = "article:" + link
        seen = r.get(akey)
    	print(akey+" seen: " + str(seen))
        #seen = False
        # unseen article
        if not seen:
            time.sleep(1)
            client.captureMessage("Getting Article",extra={
                'link': link,
            })
            
            parsed_article = parser(link)
            if parsed_article.real_article:
                process_article(parsed_article.body, link)
                r.set(akey, '1')


start_time = time.time()

#process_links(['https://www.nytimes.com/2022/04/01/learning/word-of-the-day-oblivionaire.html'])
process_links(parser.feed_urls())
#process_links(['https://www.nytimes.com/2019/11/06/magazine/turtleneck-man-bbc-question-time-brexit.html'])
record.close() 



elapsed_time = time.time() - start_time
print('Time Elapsed (seconds):')
print(elapsed_time)


