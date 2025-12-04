import unittest
from parsers.parse_fns import custom_parent
from parsers.utils import grab_url
import os

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
