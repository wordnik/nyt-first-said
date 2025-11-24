from bs4 import BeautifulSoup, NavigableString, Comment
from functools import reduce
import logging
import operator
import time
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# parser_fns need to take an html string and return an object with body and meta keys and, optionally, the soup instance.

def article_based(html, get_additional_p_tags = None):
    # print("Working on html")
    # print(html)

    # if it's not a str, decode it:
    if not isinstance(html, str):
        html = html.decode("utf-8")
        
    soup = BeautifulSoup(html, "lxml")

    for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
        comment.extract()

    meta = soup.find_all("meta")

    try:
        article = soup.find("article")
        if not article:
            logging.info("No article in html.")
            return

        logging.info("Article found in html.")
        p_tags = list(article.find_all("p"))
    except Exception as e:
        logging.info(f"Error {e} while parsing html: {html}")
        return

    if get_additional_p_tags:
        p_tags += get_additional_p_tags(soup)

    p_contents = reduce(
        operator.concat, [p.contents + [NavigableString("\n")] for p in p_tags], []
    )

    body_strings = []
    for node in p_contents:
        if type(node) is NavigableString:
            body_strings.append(node)
        else:
            if node.name == "br":
                body_strings.append(" \n ")
            else:
                try:
                    body_strings.append(node.get_text())
                except:
                    body_strings.append(node)

    body = "".join(body_strings)

    return { "body": body, "meta": meta, "soup": soup }

def get_nyt_footer_ptags(soup):
    div = soup.find(
        "div", attrs={"class": "story-addendum story-content theme-correction"}
    )
    p_tags = []

    if div:
        p_tags += [div]
    footer = soup.find("footer", attrs={"class": "story-footer story-content"})
    if footer:
        logger.debug("Found nyt footer.")
        p_tags += list(
            footer.find_all(
                lambda x: x.get("class") != "story-print-citation" and x.name == "p"
            )
        )
    return p_tags

def parse_nyt_data(data_dict):
    article = data_dict.get("data", {}).get("article", {})
    content_array = article.get("sprinkledBody", {}).get("content", [])
    paragraph_block_contents = []
    for content in content_array:
        if content.get("__typename", "") == "ParagraphBlock":
            paragraph_block_contents.append(content.get("content", {}))

    body_text = ""
    for block in paragraph_block_contents:
        for item in block:
            if item.get("__typename", "") == "TextInline":
                body_text += item.get("text", "")

    meta = {
            "documentTitle": article.get("headline", {}).get("default", ""),
            "documentId": article.get("id", ""),
            "description": article.get("summary", ""),
            "subjects": [tag.get("displayName", "") for tag in article.get("timesTags")],
            "pubDate": article.get("firstPublished", ""),
            "author": ",".join([b.get("renderedRepresentation", "") for b in article.get("bylines", [])])
            }

    return {"body": body_text, "meta": meta }

def nyt_browser(page):
    page.wait_for_load_state("domcontentloaded")
    window_globals = page.evaluate("Object.keys(window).filter(k => k.startsWith('_'))")
    print(f"Globals: {window_globals}")
    # page.wait_for_function("() => window.__preloadedData !== undefined")

    page.locator('#site-content')
    print("Saw site-content.")

    page.screenshot(path="meta/" + page.url.replace("/", "_") + ".png")
    # On a laptop, this works.
    # In the GitHub Actions container, we get: playwright._impl._errors.Error: Page.evaluate: TypeError: undefined is not an object (evaluating 'window.__preloadedData.initialData')
    # article_content_paragraphs = page.evaluate("window.__preloadedData.initialData.data.article.sprinkledBody.content.filter(o => o.__typename === 'ParagraphBlock').map(b => b.content).flat().map(c => c.text)")
    # metadata = page.evaluate("({ documentTitle: window.__preloadedData.initialData.data.article.headline.default, documentId: window.__preloadedData.initialData.data.article.id, description: window.__preloadedData.initialData.data.article.summary, subjects: window.__preloadedData.initialData.data.article.timesTags.map(t => t.displayName), pubDate: window.__preloadedData.initialData.data.article.firstPublished, author: window.__preloadedData.initialData.data.article.bylines.map(b => b.renderedRepresentation).join(',') })")
    # return { "body": article_content_paragraphs, "meta": metadata }

    # Fortunately, we can still get __preloadedData.initialData, so we'll just
    # process it in Python.
    # initialData = page.evaluate("window.__preloadedData.initialData")
    # print(f"__preloadedData.initialData: {json.dumps(initialData)}")
    # scriptLocator = page.get_by_text('window.__preloadedData');
    # initialData = scriptLocator.text_content()
    initialData = page.content()
    print("text_content", initialData)
    return parse_nyt_data(initialData)

parse_fns = {
    "article_based": article_based,
    "nyt_browser": nyt_browser
}
