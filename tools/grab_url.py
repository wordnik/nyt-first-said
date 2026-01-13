import argparse
import sys

sys.path.append('.')
from parsers.utils import grab_url

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--url', type=str, required=True, help="URL to grab contents from")
args = parser.parse_args()

contents = grab_url(args.url)
print(contents)


