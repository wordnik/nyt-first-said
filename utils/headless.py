from playwright.sync_api import sync_playwright

# This class tries to keep only one browser, context, and page around at a time.
class HeadlessBrowser():
    def __init__(self):
        playwright = sync_playwright().start()
        firefox = playwright.firefox
        self.browser = firefox.launch()
        self.context = None
        self.page = None

    def close(self):
        self.browser.close()
        self.browser = None

    def get_page(self, url):
        if not self.browser:
            raise ChildProcessError("Browser not initialized (probably deinitialized).")

        if self.page:
            self.page.close()
            self.page = None

        if self.context:
            self.context.close()
            self.context = None

        self.context = self.browser.new_context(user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0")
        self.page = self.context.new_page()
        # page.goto("https://www.nytimes.com/2025/11/13/arts/design/wifredo-lam-retrospective-moma.html")
        self.page.goto(url)
        # page.screenshot(path="screenshot.png")
        return self.page
