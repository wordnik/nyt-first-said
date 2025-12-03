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
import argparse
from datetime import date
from textblob import TextBlob 
import boto3
import urllib.request as urllib2
from utils.word_count_cache import WordCountCache
from utils.bloom_filter import BloomFilter
from utils.summary import add_summary_line
from utils.headless import HeadlessBrowser
from utils.errors import ConfigError
from parsers.api_check import does_example_exist
from parsers.utils import fill_out_sentence_object, clean_text, grab_url, get_feed_urls, split_words_by_unicode_chars
from parsers.parse_fns import parse_fns
from parsers.archive_bounce import download_via_archive

articles_processed = 0
new_words_found = 0
today = date.today()
s3 = boto3.client("s3")
enable_redis = False
bloom_filter = BloomFilter(size=26576494, num_hashes=10)
bloom_filter.load("data/bloom_filter.bits")
browser = HeadlessBrowser()

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

def post(word, article_url, sentence, meta):
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
        add_summary_line(f"New word: {sentence_obj['word']}. Example: {sentence_obj['text']}")
        obj_path = word + ".json"
        s3.put_object(Bucket="nyt-said-sentences", Key=obj_path,
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

def remove_punctuation(text):
    return re.sub(r"’s", "", re.sub(r"\p{P}+$", "", re.sub(r"^\p{P}+", "", text)))

def process_article(content, article, meta):
    global articles_processed

    # record = open("records/"+article.replace("/", "_")+".txt", "w+")
    record.write("\nARTICLE:" + article)
    print("Processing Article")
    text = clean_text(str(content))
    sentence_blob = TextBlob(text)
    for sentence in sentence_blob.sentences:
        for token in sentence.tokens:
            # TODO: New inner loop with word split among tokens.
            words = split_words_by_unicode_chars(remove_punctuation(token.string))
            for word in words:
                if len(word) < 2:
                    continue
                record.write("\n" + word)
                record.write("~" + word)
                if bloom_filter.contains(word):
                    # print("Word is in Bloom filter: {}.".format(word))
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
    articles_processed += 1

def process_links(links):
    for link in links:
        akey = "article:" + link
        seen = r.get(akey)
        link = link.replace("http://", "https://")

        #    	print(akey+" seen: " + str(seen))
        # seen = False
        # unseen article
        if not seen:
            time.sleep(5)
            print("Getting Article {}".format(link))

            if site.get("use_headless_browser", False):
                process_with_browser(url=link, site=site, akey=akey)
            else:
                process_with_request(link=link, site=site, akey=akey)

def process_with_request(link, site, akey):
    content_url = link
    if site["use_archive"]:
        print(f"Downloading via archive: {link}")
        dl_result = download_via_archive(link)
        if dl_result == False:
            print(f"Could not download via archive: {link}")
            return

        content_url = dl_result
        print(f"Successfully downloaded via archive: {link}, content_url: {content_url}")

    html = ""
    try:
        html = grab_url(content_url)
    except urllib2.HTTPError as e:
        if e.code == 404:
            self.real_article = False
            return 
        raise
    print("got html")

    parse = parse_fns.get(site["parser_name"], parse_fns["article_based"])
    parser_params = site.get("parser_params")
    if not parser_params:
        parser_params = {}
    parser_params.update({ "html": html }) 
    parsed = parse(**parser_params)

    if parsed: 
        body = parsed.get("body", "")
        if len(body) > 0:
            process_article(body, link, parsed.get("meta", {}))
            r.set(akey, "1")

def process_with_browser(url, site, akey):
    parse = parse_fns.get(site["parser_name"])
    if not parse:
        raise ConfigError(f"site {site.get('site', '[unnamed]')} config's {site['parser_name']} can't be found.")

    parsed = parse(browser, url)
    # print("parsed!")
    # print(parsed)
    process_article(parsed.get("body", ""), url, parsed.get("meta", {}))
    r.set(akey, "1")

start_time = time.time()
print("Started simple_scrape.")

feed_requester = grab_url
if site["use_headless_browser"]:
    feed_requester = browser.get_content

process_links(get_feed_urls(site["feeder_pages"], site["feeder_pattern"], feed_requester))
record.close()
browser.close()

elapsed_time = time.time() - start_time
add_summary_line(f"Time Elapsed (seconds): {elapsed_time}")
add_summary_line(f"Articles processed: {articles_processed}, new words found: {new_words_found}")
