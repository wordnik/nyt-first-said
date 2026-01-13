from bs4 import BeautifulSoup, NavigableString, Comment
from functools import reduce
import logging
import operator
import time
import json
import re
import boto3
from utils.summary import add_summary_line

s3 = boto3.client("s3")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def p_tags_to_body(p_tags):
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

    return "".join(body_strings)


# parser_fns need to take an html string and return an object with body and meta keys and, optionally, the soup instance.

def article_based(html, get_additional_p_tags = None):
    # if it's not a str, decode it:
    if not isinstance(html, str):
        try:
            html = html.decode("utf-8")
        except Exception as e:
            logging.info(f"Error {e} while decoding html: {html}")
            return
        
    soup = BeautifulSoup(html, "lxml")

    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
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

    body = p_tags_to_body(p_tags)

    return { "body": body, "meta": meta, "soup": soup }

def custom_parent(html, parent_selector):
    # if it's not a str, decode it:
    if not isinstance(html, str):
        html = html.decode("utf-8")
    
    body = ""
    soup = BeautifulSoup(html, "lxml")
    meta = soup.find_all("meta")

    try:
        article = soup.select_one(parent_selector)
        if not article:
            logging.info("No article in html.")
            return

        logging.info("Article found in html.")
        p_tags = list(article.find_all("p"))
        body = p_tags_to_body(p_tags)
    except Exception as e:
        logging.info(f"Error {e} while parsing html: {html}")
        return

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
    if not data_dict:
        return {"body": "", "meta": {}}

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
            "subjects": [tag.get("displayName", "") for tag in article.get("timesTags", {})],
            "pubDate": article.get("firstPublished", ""),
            "author": ",".join([b.get("renderedRepresentation", "") for b in article.get("bylines", [])])
            }

    return {"body": body_text, "meta": meta }

def nyt_browser(browser, url):
    page = browser.get_page(url, enable_js=False)
    page.wait_for_load_state("domcontentloaded")
    window_globals = page.evaluate("Object.keys(window).filter(k => k.startsWith('_'))")
    print(f"Globals: {window_globals}")
    # page.wait_for_function("() => window.__preloadedData !== undefined")

    page.locator('#site-content')
    print("Saw site-content.")

    # On a laptop, this works.
    # In the GitHub Actions container, we get: playwright._impl._errors.Error: Page.evaluate: TypeError: undefined is not an object (evaluating 'window.__preloadedData.initialData')
    # article_content_paragraphs = page.evaluate("window.__preloadedData.initialData.data.article.sprinkledBody.content.filter(o => o.__typename === 'ParagraphBlock').map(b => b.content).flat().map(c => c.text)")
    # metadata = page.evaluate("({ documentTitle: window.__preloadedData.initialData.data.article.headline.default, documentId: window.__preloadedData.initialData.data.article.id, description: window.__preloadedData.initialData.data.article.summary, subjects: window.__preloadedData.initialData.data.article.timesTags.map(t => t.displayName), pubDate: window.__preloadedData.initialData.data.article.firstPublished, author: window.__preloadedData.initialData.data.article.bylines.map(b => b.renderedRepresentation).join(',') })")
    # return { "body": article_content_paragraphs, "meta": metadata }

    # Fortunately, we can still get __preloadedData.initialData, so we'll just
    # process it in Python.
    content = page.content()
    matches = re.findall(r'<script>window\.__preloadedData = (.*);</script>', content)
    if len(matches) < 1:
        print("Could not find __preloadedData.")
        return {"body": "", "meta": {}}

    preloaded_data_text = matches[0]
    preloaded_data_text = preloaded_data_text.replace('undefined', 'null')
    # print("preloaded_data_text", preloaded_data_text)
    preloaded = json.loads(preloaded_data_text)
                         
    return parse_nyt_data(preloaded.get("initialData", {}))

# Warning: This depends on the browser not having closed the page or navigated away.
# Redesign if this can no longer be depended on.
def browser_report_failure(browser, url):
    shot_path = "failed_parse_" + url.replace("/", "_") + ".png"
    image = browser.screenshot(shot_path)
    s3.put_object(Bucket="nyt-said-failure-reports", Key=shot_path, Body=image, ContentType="image/png")
    add_summary_line(f"browser_article_based parser failed to get content from {url}. See screenshot at s3://nyt-said-failure-report/{shot_path}.")

def browser_article_based(browser, url):
    parsed = article_based(browser.get_content(url))
    if parsed == None:
        return {"body": "", "meta": {}, "report_failure_fn": browser_report_failure }
    return parsed

parse_fns = {
    "article_based": article_based,
    "custom_parent": custom_parent,
    "nyt_browser": nyt_browser,
    "browser_article_based": browser_article_based,

    # This is not an actual parser.
    "browser_report_failure": browser_report_failure
}
