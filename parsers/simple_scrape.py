# -*- coding: utf-8 -*-
#!/usr/bin/python
import sys
import redis
import string
import regex as re
import time
import langid
import os
from api_check import check_api
from nyt import NYTParser
from datetime import date
import json
from textblob import TextBlob 

today = date.today()

r = redis.StrictRedis(host="localhost", port=6379, db=0)

parser = NYTParser

date = today.strftime("%B-%d-%Y")

# Assuming we're running from the project root.
record = open("records/" + date + ".txt", "a+")

# common_words_text = open("data/wordlist-20210729.txt", "r").read();
# common_words = [word.lstrip('"').rstrip('"') for word in common_words_text.split("\n")]
common_words_text = open("data/nltk-stop-words.json", "r").read()
common_words = json.loads(common_words_text)

def humanize_url(article):
    return article.split("/")[-1].split(".html")[0].replace("-", " ")


def check_word(word, article_url, sentence):
    time.sleep(1)
    print("API Checking Word: {}".format(word))
    count = check_api(word)
    if count > 1:
        print("API Rejection: {}".format(word))
        record.write("~" + "API")
        return count

    language, confidence = langid.classify(sentence)

    if language != "en":
        print("Language Rejection: {}".format(word))
    #       record.write("~" + "LANG")
    #        return count

    record.write("~" + "GOOD")
    record.write("~" + word)
    if int(r.get("recently") or 0) < 8:
        r.incr("recently")
        r.expire("recently", 60 * 30)

        post(word, article_url, sentence)
    else:
        print("Recency Rejection: {}".format(word))
    return count


def post(word, article_url, sentence):
    try:
        print('New word! "{}" occurred in: {} at {}'.format(word, sentence, article_url))
    except UnicodeDecodeError as e:
        print(e)

def ok_word(s):
    if s.endswith(".") or s.endswith("’"):  # trim trailing .
        s = s[:-1]

    if not s.islower():
        return False

    return not any(i.isdigit() or i in "(.@/#-_[" for i in s)

def word_is_common(word):
    return word in common_words

def remove_punctuation(text):
    return re.sub(r"’s", "", re.sub(r"\p{P}+$", "", re.sub(r"^\p{P}+", "", text)))

def process_article(content, article):
    # record = open("records/"+article.replace("/", "_")+".txt", "w+")
    record.write("\nARTICLE:" + article)
    print("Processing Article")
    text = str(content)
    sentence_blob = TextBlob(text)
    for sentence in sentence_blob.sentences:
        for token in sentence.tokens:
            word = remove_punctuation(token.string)
            if len(word) < 2:
                continue
            record.write("\n" + word)
            record.write("~" + word)
            if word_is_common(word):
                print("Word commonness rejection: {}.".format(word))
                continue

            if ok_word(word):
                record.write("~" + word)
                wkey = "word:" + word
                cache_count = r.get(wkey)
                if not cache_count:
                    # not in cache
                    c = check_word(word, article, sentence.string)
                    r.set(wkey, c)
                else:
                    # seen in cache
                    record.write("~" + "C")

def process_links(links):
    for link in links:
        akey = "article:" + link
        seen = r.get(akey)
        link = link.replace("http://", "https://")

        #    	print(akey+" seen: " + str(seen))
        # seen = False
        # unseen article
        if not seen:
            time.sleep(30)
            print("Getting Article {}".format(link))

            parsed_article = parser(link)
            print("Is {} real_article: {}".format(link, parsed_article.real_article))
            if parsed_article.real_article:
                process_article(parsed_article.body, link)
                r.set(akey, "1")


start_time = time.time()
print("Started simple_scrape.")
process_links(parser.feed_urls())
record.close()


elapsed_time = time.time() - start_time
print("Time Elapsed (seconds):")
print(elapsed_time)
