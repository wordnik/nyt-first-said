import uuid
import re
import socket
from bs4 import BeautifulSoup
import http.cookiejar as cookielib
import urllib
import time
import logging

def get_meta_content_by_attr(bs_meta_list, attr, val, default=None):
    # print("name: {}".format(bs_meta_list.name))
    for element in bs_meta_list:
        attr_val = element.attrs.get(attr, None)
        if attr_val != None and attr_val == val:
            return element.get("content")
    return default

def fill_out_sentence_object(word, sentence, article_url, date, meta, api):
    sentence_obj = {
        "metadata": {
            "searchAPI": api,
            "crawlDate": date,
            "source": article_url,
            "DOI": None,
        },
        "hypothesisAccount": "",
        "exampleType": "sentence",
        "rating": 1,
        "url": article_url,
        "text": sentence,
        "frd_rating": 1,
        "exampleId": str(uuid.uuid4()),
        "word": word,
        "labels": [],
        "fileId": "",
    }

    metadata = sentence_obj["metadata"]

    if type(meta) == dict:
        for key in ["documentTitle", "documentId", "description", "subjects"]:
            metadata[key] = meta[key]

        sentence_obj["pubDate"] = meta["pubDate"]
        sentence_obj["author"] = meta["author"]
    else:
        # meta is a Beautiful Soup element list in this case.
        metadata["documentTitle"] = get_meta_content_by_attr(meta, "property", "og:title")
        metadata["documentId"] = get_meta_content_by_attr(meta, "name", "articleId", article_url)
        metadata["description"] = get_meta_content_by_attr(meta, "property", "og:description")
        metadata["subjects"] = get_meta_content_by_attr(meta, "name", "news_keywords".split(","), [])
        sentence_obj["pubDate"] = get_meta_content_by_attr(meta, "property", "article:published_time")
        sentence_obj["author"] = get_meta_content_by_attr(meta, "name", "byl")

    return sentence_obj

def remove_ending_punc(s):
    return re.sub(r'([.\?!;:]+)$', '', s)

def clean_text(text):
    # u200b is a zero-width space (https://en.wikipedia.org/wiki/Zero-width_space)
    # that trips up TextBlob.
    return text.replace(u'\u200b', ' ')

def find_pos_for_word(pos_tags, word):
    try:
        pos_tuple = next(x for x in pos_tags if remove_ending_punc(x[0]) == word)
        if pos_tuple:
            return pos_tuple[1]
    except StopIteration as e:
        print("Could not find {} in {}".format(word, pos_tags))
        return None

def make_url_safe(url):
    parsed = urllib.parse.urlparse(url)
    return parsed._replace(path=parsed.path.replace(" ", "%20")).geturl()

def grab_url(url, max_depth=5, opener=None):
    if opener is None:
        cj = cookielib.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    retry = False
    url = make_url_safe(url) 
    logging.info("grabbing " + url)
    try:
        text = opener.open(url, timeout=10).read()
        if b"<title>NY Times Advertisement</title>" in text:
            logging.info("advert retry")
            retry = True
    except socket.timeout:
        logging.info("socket retry")
        retry = True
    except urllib.error.HTTPError as e:
        logging.info(url)
        logging.info("http error retry")
        logging.info(e.reason)
        retry = True
    except Exception as e:
        logging.info(f"Error {e} while opening {url}.")
        return ""

    if max_depth == 0:
        logging.info("bad url")
        return ""

    if retry:
        #        if max_depth == 0:
        #            raise Exception('Too many attempts to download %s' % url)
        time.sleep(5.0)
        return grab_url(url, max_depth - 1, opener)
    return text


def concat(domain, url):
    return domain + url if url.startswith("/") else domain + "/" + url

def get_feed_urls(feeder_pages, feeder_pattern, requester=grab_url):
    all_urls = []
    for feeder_url in feeder_pages:
        if feeder_url.find(":") == -1:
            # No protocol. Assume https.
            feeder_url = "https://" + feeder_url
        html = requester(feeder_url)
        soup = BeautifulSoup(html, "html5lib")

        # "or ''" to make None into str
        urls = [a.get("href") or "" for a in soup.find_all("a")]

        # If no http://, prepend domain name
        domain = "/".join(feeder_url.split("/")[:3])
        urls = [url if "://" in url else concat(domain, url) for url in urls]
        all_urls = all_urls + [
            url for url in urls if re.search(feeder_pattern, url)
        ]
    return all_urls

# This is to cover word delimiters not covered by TextBlob.
def split_words_by_unicode_chars(s):
    # Unicode symbol range https://en.wikipedia.org/wiki/List_of_Unicode_characters#Unicode_symbols
    return [x for x in re.split('[\u2013-\u204a]', s) if x != '']

