# -*- coding: utf-8 -*-
#!/usr/bin/python
import sys
import redis
import string
import regex as re
import time
import langid
import requests
import os
from api_check import check_api
from nyt import NYTParser
from datetime import date

today = date.today()

r = redis.StrictRedis(host="localhost", port=6379, db=0)

parser = NYTParser

date = today.strftime("%B-%d-%Y")

# Assuming we're running from the project root.
record = open("records/" + date + ".txt", "a+")


def humanize_url(article):
    return article.split("/")[-1].split(".html")[0].replace("-", " ")


def check_word(word, article_url, word_context):
    time.sleep(1)
    print(word)
    print("API Checking Word")
    count = check_api(word)
    if count > 1:
        print("API Rejection")
        record.write("~" + "API")
        return count

    language, confidence = langid.classify(word_context)

    if language != "en":
        print("Language Rejection")
    #       record.write("~" + "LANG")
    #        return count

    record.write("~" + "GOOD")
    record.write("~" + word)
    if int(r.get("recently") or 0) < 8:
        r.incr("recently")
        r.expire("recently", 60 * 30)

        post(word, article_url, word_context)
    else:
        print("Recency Rejection")
    return count


def post(word, article_url, word_context):
    try:
        print('"{}" occurred in: {} at {}'.format(word, word_context, article_url))
    except UnicodeDecodeError as e:
        print(e)

def ok_word(s):
    if s.endswith(".") or s.endswith("’"):  # trim trailing .
        s = s[:-1]

    if not s.islower():
        return False

    return not any(i.isdigit() or i in "(.@/#-_[" for i in s)


def remove_punctuation(text):
    return re.sub(r"’s", "", re.sub(r"\p{P}+$", "", re.sub(r"^\p{P}+", "", text)))


def normalize_punc(raw_word):
    replaced_chars = [
        ",",
        "—",
        "”",
        "“",
        ":",
        "'",
        "’s",
        '"',
        "\u200B",
        "\u200E",
        "\u200C",
    ]
    for char in replaced_chars:
        raw_word = raw_word.replace(char, " ")

    raw_word = raw_word.replace("\u00AD", "-")

    return raw_word.split(" ")


def context(content, word):
    loc = content.find(word)
    to_period = content[loc:].find(".")
    prev_period = content[:loc].rfind(".")
    allowance = 70
    if to_period < allowance:
        end = content[loc : loc + to_period + 1]
    else:
        end = "{}…".format(content[loc : loc + allowance])

    if loc - prev_period < allowance:
        start = "{} ".format(content[prev_period + 2 : loc].strip())
    else:
        start = "…{}".format(content[loc - allowance : loc])

    return "{}{}".format(start, end)


def process_article(content, article):
    # record = open("records/"+article.replace("/", "_")+".txt", "w+")
    record.write("\nARTICLE:" + article)
    text = str(content)
    words = text.split()
    #    print(words)
    print("Processing Article")
    for raw_word_h in words:
        for raw_word in normalize_punc(raw_word_h):
            if len(raw_word) < 2:
                continue
            record.write("\n" + raw_word)
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
        link = link.replace("http://", "https://")

        #    	print(akey+" seen: " + str(seen))
        # seen = False
        # unseen article
        if not seen:
            time.sleep(30)
            print("Getting Article")

            parsed_article = parser(link)
            print(parsed_article.real_article)
            if parsed_article.real_article:
                process_article(parsed_article.body, link)
                r.set(akey, "1")


start_time = time.time()
process_links(parser.feed_urls())
record.close()


elapsed_time = time.time() - start_time
print("Time Elapsed (seconds):")
print(elapsed_time)
