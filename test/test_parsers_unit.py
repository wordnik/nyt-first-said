import unittest
from parsers.parse_fns import custom_parent, article_based
from parsers.utils import grab_url
import os
import urllib

class ParsersSuite(unittest.TestCase):
    def test_farmersjournal(self):
        self.maxDiff = None
        with open("test/fixtures/farmersjournal-example-contents.txt") as f:
            expected_contents = f.read()
            f.close()
        with open("test/fixtures/farmersjournal-example.html") as f:
            parsed = custom_parent(html = f.read(), parent_selector = "#article-body-gshowcase")
            self.assertEqual(parsed["body"], expected_contents)
            f.close()

    def test_sheppnews(self):
        self.maxDiff = None
        with open("test/fixtures/sheppnews-article-contents.txt") as f:
            expected_contents = f.read()
            f.close()
        with open("test/fixtures/sheppnews-article.html") as f:
            parsed = article_based(html = f.read())
            # with open("test/fixtures/sheppnews-article-contents.txt", "w", encoding="utf-8") as out:
            #     out.write(parsed["body"])
            #     out.close()
            self.assertEqual(parsed["body"], expected_contents)
            f.close()

    def test_redirect(self):
        with self.assertRaises(urllib.error.HTTPError):
            # Raises error because the url redirects to a different domain.
            grab_url("https://naij.com")

        redirect_content = grab_url("https://www.geeksofdoom.com/2026/03/18/spring-2026-book-recommendations-gifts")
        self.assertTrue(len(redirect_content) > 100, "Returns text because the url redirects but not to a different domain.")
