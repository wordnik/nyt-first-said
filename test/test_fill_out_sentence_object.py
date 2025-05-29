import unittest
from utils import fill_out_sentence_object
from bs4 import BeautifulSoup

example_nyt_html = open("test/fixtures/example-nyt-page.html", "r").read()

class SentenceObjectSuite(unittest.TestCase):
  def test_basic(self):
    soup = BeautifulSoup(example_nyt_html, "lxml")
    meta = soup.find_all("meta")
    sentence_obj = fill_out_sentence_object(
        word = "naïve",
        sentence = "In a show that recently opened at the LaMaMa Experimental Theater Club in the East Village, a group of actors led by a young, ambitious, charmingly naïve director are almost finished rehearsing Chekhov’s “The Seagull” at the famed Moscow Art Theater when Russia invades Ukraine.", 
        article_url = "https://www.nytimes.com/2025/05/28/opinion/trump-danger-normalization-shock.html",
        date = "2025-05-28",
        meta = meta
    )
    expected_sentence_obj = {'metadata': {'searchAPI': 'nyt', 'documentTitle': None, 'crawlDate': '2025-05-28', 'documentId': None, 'description': None, 'source': 'https://www.nytimes.com/2025/05/28/opinion/trump-danger-normalization-shock.html', 'DOI': None, 'subjects': None}, 'pubDate': None, 'author': None, 'hypothesisAccount': '', 'exampleType': '', 'rating': 1, 'url': 'https://www.nytimes.com/2025/05/28/opinion/trump-danger-normalization-shock.html', 'text': 'In a show that recently opened at the LaMaMa Experimental Theater Club in the East Village, a group of actors led by a young, ambitious, charmingly naïve director are almost finished rehearsing Chekhov’s “The Seagull” at the famed Moscow Art Theater when Russia invades Ukraine.', 'frd_rating': 1, 'exampleId': '', 'word': 'naïve', 'labels': [], 'fileId': ''}
     
    self.assertEqual(sentence_obj, expected_sentence_obj)

if __name__ == '__main__':
    unittest.main()
