import unittest
from parsers.parse_fns import parse_fns
from parsers.utils import grab_url
import json
import jellyfish
from utils.headless import HeadlessBrowser

class ParsersSuite(unittest.TestCase):
    def test_farmersjournal(self):
        self.maxDiff = None
        with open("test/fixtures/farmersjournal-example-contents.txt") as f:
            expected_contents = f.read()
            f.close()
        html = grab_url("https://www.farmersjournal.ie/beef/markets/beef-trends-cattle-shortage-pushing-prices-upwards-892318")

        with open("data/target_sites.json", "r") as f:
            target_sites_text = f.read()
            f.close()

        target_sites = json.loads(target_sites_text)
        site = target_sites.get("farmersjournal")
        parse = parse_fns.get(site.get("parser_name"))
        parser_params = site.get("parser_params")
        parser_params.update({ "html": html }) 

        parsed = parse(**parser_params)
        # print(parsed["body"])
        self.assertTrue(jellyfish.levenshtein_distance(parsed["body"], expected_contents) < 0.1, "Parser gets close to expected body from live content.")

    def test_sciam(self):
        self.maxDiff = None
        with open("test/fixtures/sciam-example-contents.txt") as f:
            expected_contents = f.read()
            f.close()

        html = grab_url("https://www.scientificamerican.com/article/how-bad-will-flu-season-be-this-year/")

        with open("data/target_sites.json", "r") as f:
            target_sites_text = f.read()
            f.close()

        target_sites = json.loads(target_sites_text)
        site = target_sites.get("sciam")
        parse = parse_fns.get(site.get("parser_name"))
        parser_params = site.get("parser_params", {})
        parser_params.update({ "html": html }) 

        parsed = parse(**parser_params)
        # with open("test/fixtures/sciam-example-contents.txt", "w") as out:
        #     out.write(parsed["body"])
        #     out.close()
        distance = jellyfish.levenshtein_distance(parsed["body"], expected_contents)
        print("distance:", distance)
        self.assertTrue(distance < 2, "Parser gets close to expected body from live content.")

    def test_nyt_contents_page(self):
        self.maxDiff = None
        # with open("test/fixtures/sciam-example-contents.txt") as f:
        #     expected_contents = f.read()
        #     f.close()

        # html = grab_url("")

        with open("data/target_sites.json", "r") as f:
            target_sites_text = f.read()
            f.close()

        browser = HeadlessBrowser()
        target_sites = json.loads(target_sites_text)
        site = target_sites.get("nyt")
        parse = parse_fns.get(site.get("parser_name"))
        parser_params = site.get("parser_params", {})
        parser_params.update({ "browser": browser }) 
        parser_params.update({ "url": "https://www.nytimes.com/#site-content" }) 

        parsed = parse(**parser_params)
        self.assertEqual(parsed["body"], "", "Gets no content but does not cash.")
