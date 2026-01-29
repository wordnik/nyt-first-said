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

    def test_lawyersweekly_page(self):
        self.maxDiff = None

        with open("data/target_sites.json", "r") as f:
            target_sites_text = f.read()
            f.close()
        with open("test/fixtures/lawyersweekly-example-contents.txt") as f:
            expected_contents = f.read()
            f.close()

        html = grab_url("https://lawyersweekly.com.au/sme-law/43536-expelled-barrister-accused-of-launching-collateral-attack-on-firm")
        target_sites = json.loads(target_sites_text)
        site = target_sites.get("lawyersweekly_com_au")
        parse = parse_fns.get(site.get("parser_name"))
        parser_params = site.get("parser_params", {})
        parser_params.update({ "html": html }) 

        parsed = parse(**parser_params)
        # print(parsed["body"])
        self.assertTrue(jellyfish.levenshtein_distance(parsed["body"], expected_contents) < 0.1, "Parser gets close to expected body from live content.")
    def test_dailycaller(self):
        self.maxDiff = None

        with open("data/target_sites.json", "r") as f:
            target_sites_text = f.read()
            f.close()
        with open("test/fixtures/dailycaller-example-contents.txt") as f:
            expected_contents = f.read()
            f.close()

        target_sites = json.loads(target_sites_text)
        site = target_sites.get("dailycaller_com")
        parse = parse_fns.get(site.get("parser_name"))
        parser_params = site.get("parser_params", {})
        # html = grab_url("https://dailycaller.com/2026/01/20/mamdani-ice-abolished-the-view/")
        # with open("test/fixtures/dailycaller-example-contents.html", "wb") as out:
        #     out.write(html)
        #     out.close()
        with open("test/fixtures/dailycaller-example-contents.html") as f:
            html = f.read()
            f.close()
        parser_params.update({ "html": html }) 

        parsed = parse(**parser_params)
        print(parsed["body"])
        self.assertEqual(parsed["body"].strip(), expected_contents.strip(), "Parser gets close to expected body from content.")
        # with open("test/fixtures/dailycaller-example-contents.txt", "w") as out:
        #     out.write(parsed["body"])
        #     out.close()
