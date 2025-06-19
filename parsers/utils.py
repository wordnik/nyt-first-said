import uuid
import re

def get_meta_content_by_attr(bs_meta_list, attr, val):
    # print("name: {}".format(bs_meta_list.name))
    for element in bs_meta_list:
        attr_val = element.attrs.get(attr, None)
        if attr_val != None and attr_val == val:
            return element.get("content")

def fill_out_sentence_object(word, sentence, article_url, date, meta, pos):
    return {
        "metadata": {
            "searchAPI": "nyt",
            "documentTitle": get_meta_content_by_attr(meta, "property", "og:title"),
            "crawlDate": date,
            "documentId": get_meta_content_by_attr(meta, "name", "articleId"),
            "description": get_meta_content_by_attr(meta, "property", "og:description"),
            "source": article_url,
            "DOI": None,
            "subjects": get_meta_content_by_attr(meta, "name", "news_keywords")
        },
        "pubDate": get_meta_content_by_attr(meta, "property", "article:published_time"),
        "author": get_meta_content_by_attr(meta, "name", "byl"),
        "hypothesisAccount": "",
        "exampleType": "",
        "rating": 1,
        "url": article_url,
        "text": sentence,
        "frd_rating": 1,
        "exampleId": str(uuid.uuid4()),
        "word": word,
        "labels": [],
        "fileId": "",
        "pos": pos
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
