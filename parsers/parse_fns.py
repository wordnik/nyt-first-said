from bs4 import BeautifulSoup, NavigableString, Comment
from functools import reduce
import logging
import operator
import time

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

def nyt_browser(page):
    page.wait_for_load_state("domcontentloaded")
    window_globals = page.evaluate("Object.keys(window).filter(k => k.startsWith('_'))")
    print("Globals: {window_globals}")

    time.sleep(30)
    article_content_paragraphs = page.evaluate("window.__preloadedData.initialData.data.article.sprinkledBody.content.filter(o => o.__typename === 'ParagraphBlock').map(b => b.content).flat().map(c => c.text)")
    metadata = page.evaluate("({ documentTitle: window.__preloadedData.initialData.data.article.headline.default, documentId: window.__preloadedData.initialData.data.article.id, description: window.__preloadedData.initialData.data.article.summary, subjects: window.__preloadedData.initialData.data.article.timesTags.map(t => t.displayName), pubDate: window.__preloadedData.initialData.data.article.firstPublished, author: window.__preloadedData.initialData.data.article.bylines.map(b => b.renderedRepresentation).join(',') })")
    return { "body": ' '.join(article_content_paragraphs), "meta": metadata }

parse_fns = {
    "article_based": article_based,
    "nyt_browser": nyt_browser
}
