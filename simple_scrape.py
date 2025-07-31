# -*- coding: utf-8 -*-
#!/usr/bin/python
import sys
import redis
import string
import regex as re
import time
import langid
import os
import json
from datetime import date
from textblob import TextBlob 
import boto3

from parsers.api_check import does_example_exist
from parsers.nyt import NYTParser
from parsers.utils import fill_out_sentence_object, clean_text

today = date.today()
s3 = boto3.client("s3")

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

# Returns whether or not this example exists (as a 0 or 1). Even if the method
# ends up posting the word, it may not make it all the way through the example
# pipeline, so we return False in that case.
def check_word(word, article_url, sentence, meta):
    time.sleep(1)
    print("API Checking Word: {}".format(word))
    
    example_exists = does_example_exist(word)
    if example_exists:
        print("We already have an example for {}".format(word))
        record.write("~" + "API")
        return example_exists 

    language, confidence = langid.classify(sentence)

    if language != "en":
        print("Language Rejection: {}".format(word))

    record.write("~" + "GOOD")
    record.write("~" + word)
    if int(r.get("recently") or 0) < 8:
        r.incr("recently")
        r.expire("recently", 60 * 30)

        post(word, article_url, sentence, meta)
    else:
        print("Recency Rejection: {}".format(word))

    return example_exists 

def post(word, article_url, sentence, meta):
    try:
        sentence_obj = fill_out_sentence_object(
            word=word,
            sentence=sentence,
            article_url=article_url,
            date=date,
            meta=meta,
        )
        sentence_json = json.dumps(sentence_obj, indent=2)
        print('New word! {}'.format(sentence_json))
        obj_path = word + ".json"
        s3.put_object(Bucket="nyt-said-sentences", Key=obj_path,
                      Body=sentence_json.encode())
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

def process_article(content, article, meta):
    # record = open("records/"+article.replace("/", "_")+".txt", "w+")
    record.write("\nARTICLE:" + article)
    print("Processing Article")
    text = clean_text(str(content))
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
                cache_flag = r.get(wkey)
                if cache_flag:
                    # seen in cache
                    record.write("~" + "C")
                else:
                    # not in cache
                    # NLTK part of speech tag list: https://stackoverflow.com/a/38264311/87798
                    # Multiply by 1 to cast the boolean into a number.
                    r.set(
                        wkey,
                        1 * check_word(word, article, sentence.string, meta))

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
                process_article(parsed_article.body, link, parsed_article.meta)
                r.set(akey, "1")
start_time = time.time()
print("Started simple_scrape.")
process_links(parser.feed_urls())
record.close()


elapsed_time = time.time() - start_time
print("Time Elapsed (seconds):")
print(elapsed_time)

