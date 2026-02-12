import sys
sys.path.append('.')
from utils.headless import HeadlessBrowser 

browser = HeadlessBrowser()

def search(term):
    page = browser.get_page("https://html.duckduckgo.com/html/?q=" + term)
    result = page.locator("#links .web-result").nth(0)
    link = result.locator(".result__title a")
    outbound_url = link.get_attribute("href")
    print(outbound_url)
    link.click()
    page.wait_for_load_state(timeout = 10 * 60 * 1000)
    # page.wait_for_url("(?!https:\/\/duckduckgo\.com)")
    return page.url

