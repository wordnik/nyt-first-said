# -*- coding: utf-8 -*-
#!/usr/bin/python
import sys
import redis
import string
import time
import langid
import os
import json
import argparse
from datetime import date
from textblob import TextBlob 
import boto3
import urllib.request as urllib2
import random
import logging

from utils.word_count_cache import WordCountCache
from utils.bloom_filter import BloomFilter
from utils.summary import add_summary_line
from utils.headless import HeadlessBrowser
from utils.errors import ConfigError
from utils.uninteresting_words import get_uninteresting_count_for_word, increment_uninteresting_count_for_word
from utils.url_visits import log_url_visit, was_url_visited
from utils.text_cleaning import remove_punctuation, remove_trouble_characters, has_username
from parsers.api_check import does_example_exist
from parsers.utils import fill_out_sentence_object, clean_text, grab_url, get_feed_urls, split_words_by_unicode_chars
from parsers.parse_fns import parse_fns
from parsers.archive_bounce import download_via_archive

articles_processed = 0
new_words_found = 0
today = date.today()
s3 = boto3.client("s3")
dynamo = boto3.client("dynamodb")
enable_redis = False
bloom_filter = BloomFilter(size=26576494, num_hashes=10)
bloom_filter.load("data/bloom_filter.bits")
browser = HeadlessBrowser()
run_count = 0
strategies_unused = [
        { "parser_name": "article_based", "parser_params": {} },
        { "parser_name": "custom_parent", "parser_params": { "parent_selector": "main" } },
        { "parser_name": "browser_article_based", "parser_params": {} },
        ]

if enable_redis:
    r = redis.StrictRedis(host="localhost", port=6379, db=0)
else:
    r = WordCountCache()

date = today.isoformat()

argparser = argparse.ArgumentParser()
argparser.add_argument('site_name')
args = argparser.parse_args()

# Open the site configs.
target_sites_text = open("data/target_sites.json", "r").read()
target_sites = json.loads(target_sites_text)
site = target_sites.get(args.site_name)

if not site:
    print("Could not find site config for " + args.site_name)
    quit()

# Assuming we're running from the project root.
record = open("records/" + date + ".txt", "a+")

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

def post(word, article_url, sentence, meta, bucket="nyt-said-sentences"):
    global new_words_found
    try:
        sentence_obj = fill_out_sentence_object(
            word=word,
            sentence=sentence,
            article_url=article_url,
            date=date,
            meta=meta,
            api=site["site"]
        )
        sentence_json = json.dumps(sentence_obj, indent=2)
        if bucket == "nyt-said-sentences":
            add_summary_line(f"New word: {sentence_obj['word']}. Example: {sentence_obj['text']}")
        else:
            logging.info(f"Uninteresting: {sentence_obj['word']}. Example: {sentence_obj['text']}")
        obj_path = word + ".json"
        s3.put_object(Bucket=bucket, Key=obj_path,
                      Body=sentence_json.encode(), ContentType="application/json")
        new_words_found += 1
    except UnicodeDecodeError as e:
        print(e)

def ok_word(s):
    if s.endswith(".") or s.endswith("’"):  # trim trailing .
        s = s[:-1]

    if not s.islower():
        return False

    return not any(i.isdigit() or i in "(.@/#-_[" for i in s)

def process_article(content, url, meta):
    global articles_processed

    uninteresting_sentence_params = []
    # record = open("records/"+url.replace("/", "_")+".txt", "w+")
    record.write("\nARTICLE:" + url)
    print("Processing Article")
    text = clean_text(str(content))
    sentence_blob = TextBlob(text)
    for sentence in sentence_blob.sentences:
        if has_username(str(sentence)):
            # If the sentence has "@word" tokens, they will parse as separate
            # "@" and "word" tokens, so we'll avoid this situation.
            continue

        for token in sentence.tokens:
            # TODO: New inner loop with word split among tokens.
            words = split_words_by_unicode_chars(
                    remove_trouble_characters(remove_punctuation(token.string))
            )
            for word in words:
                if len(word) < 2:
                    continue
                record.write("\n" + word)
                record.write("~" + word)
                if bloom_filter.contains(word):
                    # print("Word is in Bloom filter: {}.".format(word))
                    if len(uninteresting_sentence_params) < 10:
                        uninteresting_sentence_params.append({
                            "word": word,
                            "article_url": url,
                            "sentence": sentence.string,
                            "meta": meta,
                            "bucket": "uninteresting-sentences"
                        })
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
                            1 * check_word(word, url, sentence.string, meta))

    if len(uninteresting_sentence_params) > 0:
        sentence_params = random.sample(uninteresting_sentence_params, 1)[0]
        word = sentence_params.get("word").lower()
        if word and get_uninteresting_count_for_word(word) < 1000:
            post(**sentence_params)
            increment_uninteresting_count_for_word(word)
        else:
            logging.info(f"We already have 1000 sentences for {word}.")

    articles_processed += 1
    log_url_visit(url)

def process_links(links, parser_name, parser_params):
    global articles_processed
    for link in links:
        if was_url_visited(link):
            # We count it as processed because we use articles_processed as a
            # measure of success for the run. 0 articles_processed means failure.
            articles_processed += 1
            logging.info(f"Skipping {link} because we've already visited it before.")
            continue

        link = link.replace("http://", "https://")

        if link.find(":") == -1:
            # No protocol. Assume https.
            link = "https://" + link

        if not link.startswith("https://"):
            # Avoid mailto:, tel:, ftp:, etc.
            continue

        # unseen article
        time.sleep(site.get("article_pause_secs", 5))
        print("Getting Article {}".format(link))

        if parser_name.startswith("browser_") or parser_name.startswith("nyt_browser"):
            process_with_browser(url=link, site=site, parser_name=parser_name, parser_params=parser_params)
        else:
            process_with_request(link=link, site=site, parser_name=parser_name, parser_params=parser_params)

def process_with_request(link, site, parser_name, parser_params):
    content_url = link

    html = ""
    try:
        html = grab_url(content_url)
    except urllib2.HTTPError as e:
        if e.code == 404:
            self.real_article = False
            return 
        raise
    print("got html")

    parse = parse_fns.get(parser_name, parse_fns["article_based"])
    if not parser_params:
        parser_params = {}
    parser_params.update({ "html": html })
    parsed = parse(**parser_params)

    if parsed: 
        body = parsed.get("body", "")
        if len(body) > 0:
            process_article(body, link, parsed.get("meta", {}))

def process_with_browser(url, site, parser_name, parser_params):
    parse = parse_fns.get(parser_name)
    if not parse:
        raise ConfigError(f"site {site.get('site', '[unnamed]')} config's {site['parser_name']} can't be found.")

    parsed = parse(browser, url)
    # print("parsed!")
    # print(parsed)
    process_article(parsed.get("body", ""), url, parsed.get("meta", {}))

def run_brush(parser_name, parser_params):
    global run_count

    start_time = time.time()

    print(f"Started simple_scrape run {run_count}.")

    feed_requester = grab_url
    if parser_name.startswith("browser_"):
        feed_requester = browser.get_content

    process_links(
            get_feed_urls(site["feeder_pages"], site["domains"][0], feed_requester),
            parser_name,
            parser_params
            )

    elapsed_time = time.time() - start_time
    add_summary_line(f"Time Elapsed for run {run_count} (seconds): {elapsed_time}")
    add_summary_line(f"Articles processed for run {run_count}: {articles_processed}, new words found: {new_words_found}")
    run_count += 1

    site_name = site.get("site", "[unnamed]")

    if site.get("works", False) == False:
        # Report how it went.
        res = dynamo.put_item(
                TableName="nyt-said-site-results",
                Item={
                    "site": {"S": site_name},
                    "articles_processed": {"N": str(articles_processed)},
                    "succeeding_parser_name": {"S": parser_name}
                })

        if articles_processed < 1 and len(strategies_unused) > 0:
            # Try again if we didn't get anything.
            strategy = strategies_unused.pop()
            run_brush(**strategy)

run_brush(site.get("parser_name"), site.get("parser_params"))

record.close()
browser.close()
