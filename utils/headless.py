import logging
import os
from playwright.sync_api import sync_playwright

playwright = sync_playwright().start()

# This class tries to keep only one browser, context, and page around at a time.
class HeadlessBrowser():
    def __init__(self):
        launcher = playwright.firefox
        exe_path = launcher.executable_path #+ "test"
        browser_exe_exists = os.access(exe_path, os.X_OK)
        print(f"Is browser at {exe_path} there and executable? {browser_exe_exists}")
        if not browser_exe_exists:
            parent_path = os.path.dirname(exe_path)
            for i in range(3):
                parent_exists = os.access(parent_path, os.F_OK)
                print(f"{parent_path} exists?", parent_exists)
                if parent_exists:
                    print(f"Contents of {parent_path}: {os.listdir(parent_path)}")
                    break
                parent_path = os.path.dirname(parent_path)

            raise OSError(f"Browser not found or not executable at {launcher.executable_path}.")

        self.browser = launcher.launch()
        self.context = None
        self.page = None

    def close(self):
        self.browser.close()
        self.browser = None

    def get_page(self, url, enable_js=True):
        if not self.browser:
            raise ChildProcessError("Browser not initialized (probably deinitialized).")

        if self.page:
            self.page.close()
            self.page = None

        if self.context:
            self.context.close()
            self.context = None

        # TODO: Vary agent
        self.context = self.browser.new_context(
                user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0",
                java_script_enabled=enable_js
                )
        self.page = self.context.new_page()
        self.page.goto(url, timeout=60000)
        return self.page

    def get_content(self, url):
        try:
            self.get_page(url, enable_js=False)
            self.page.wait_for_load_state("domcontentloaded")
            return self.page.content()
        except Exception as e:
            logging.error(f"Error {e} while trying to get content from {url}.")
            return ""

    def screenshot(self, path_to_put_screenshot):
        if not self.browser:
            raise ChildProcessError("Browser not initialized (probably deinitialized).")

        if not self.page:
            raise ChildProcessError("No page loaded.")

        return self.page.screenshot()

