import uuid
import re
from bs4 import BeautifulSoup
import http.cookiejar as cookielib
import urllib.request as urllib2

def get_meta_content_by_attr(bs_meta_list, attr, val, default=None):
    # print("name: {}".format(bs_meta_list.name))
    for element in bs_meta_list:
        attr_val = element.attrs.get(attr, None)
        if attr_val != None and attr_val == val:
            return element.get("content")
    return default

def fill_out_sentence_object(word, sentence, article_url, date, meta):
    return {
        "metadata": {
            "searchAPI": "nyt",
            "documentTitle": get_meta_content_by_attr(meta, "property", "og:title"),
            "crawlDate": date,
            "documentId": get_meta_content_by_attr(meta, "name", "articleId", article_url),
            "description": get_meta_content_by_attr(meta, "property", "og:description"),
            "source": article_url,
            "DOI": None,
            "subjects": get_meta_content_by_attr(meta, "name", "news_keywords".split(","), [])
        },
        "pubDate": get_meta_content_by_attr(meta, "property", "article:published_time"),
        "author": get_meta_content_by_attr(meta, "name", "byl"),
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

def grab_url(url, max_depth=5, opener=None):
    if opener is None:
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    retry = False
    print("grabbing " + url)
    try:
        text = opener.open(url, timeout=10).read()
        if b"<title>NY Times Advertisement</title>" in text:
            print("advert retry")
            retry = True
    except socket.timeout:
        print("socket retry")
        retry = True
    except urllib2.HTTPError as e:
        print(url)
        print("http error retry")
        print(e.reason)
        retry = True

    if max_depth == 0:
        print("bad url")
        return ""

    if retry:
        #        if max_depth == 0:
        #            raise Exception('Too many attempts to download %s' % url)
        time.sleep(5.0)
        return grab_url(url, max_depth - 1, opener)
    return text


def concat(domain, url):
    return domain + url if url.startswith("/") else domain + "/" + url

def get_feed_urls(feeder_pages, feeder_pattern):
    all_urls = []
    for feeder_url in feeder_pages:
        html = grab_url(feeder_url)
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
