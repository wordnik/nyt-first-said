def get_meta_content_by_attr(bs_meta_list, attr, val):
    # print("name: {}".format(bs_meta_list.name))
    for element in bs_meta_list:
        attr_val = element.attrs.get(attr, None)
        if attr_val != None and attr_val == val:
            return element.get("content")

def fill_out_sentence_object(word, sentence, article_url, date, meta):
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
        "exampleId": "",
        "word": word,
        "labels": [],
        "fileId": ""
    };
