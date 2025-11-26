import unittest
from parsers.parse_fns import parse_fns
from parsers.utils import grab_url
import json

class ParsersSuite(unittest.TestCase):
    def test_farmersjournal(self):
        self.maxDiff = None
        with open("test/fixtures/farmersjournal-example-contents.txt") as f:
            expected_contents = f.read()
            f.close()
        html = grab_url("https://www.farmersjournal.ie/beef/markets/beef-trends-cattle-shortage-pushing-prices-upwards-892318")

        target_sites_text = open("data/target_sites.json", "r").read()
        target_sites = json.loads(target_sites_text)
        site = target_sites.get("farmersjournal")
        parse = parse_fns.get(site.get("parser_name"))
        parser_params = site.get("parser_params")
        parser_params.update({ "html": html }) 

        parsed = parse(**parser_params)
            # with open("test/fixtures/farmersjournal-example-contents.txt", "w") as out:
        #     out.write(parsed["body"])
        #     out.close()
        print(parsed["body"])
