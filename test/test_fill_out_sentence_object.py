import unittest
from parsers.utils import fill_out_sentence_object
from bs4 import BeautifulSoup

example_nyt_html = open("test/fixtures/example-nyt-page.html", "r").read()

class SentenceObjectSuite(unittest.TestCase):
  maxDiff = None

  def test_basic(self):
    soup = BeautifulSoup(example_nyt_html, "lxml")
    meta = soup.find_all("meta")
    sentence_obj = fill_out_sentence_object(
        word = "naïve",
        sentence = "In a show that recently opened at the LaMaMa Experimental Theater Club in the East Village, a group of actors led by a young, ambitious, charmingly naïve director are almost finished rehearsing Chekhov’s “The Seagull” at the famed Moscow Art Theater when Russia invades Ukraine.", 
        article_url = "https://www.nytimes.com/2025/05/28/opinion/trump-danger-normalization-shock.html",
        date = "2025-05-28",
        meta = meta,
        api = "nyt"
    )

    self.assertEqual(len(sentence_obj.get('exampleId', '')), 36,
                     'Sentence object has a uuid-length exampleId.');

    del sentence_obj['exampleId']
    expected_sentence_obj = {'metadata': {'searchAPI': 'nyt', 'documentTitle': None, 'crawlDate': '2025-05-28', 'documentId': 'https://www.nytimes.com/2025/05/28/opinion/trump-danger-normalization-shock.html', 'description': None, 'source': 'https://www.nytimes.com/2025/05/28/opinion/trump-danger-normalization-shock.html', 'DOI': None, 'subjects': []}, 'pubDate': None, 'author': None, 'hypothesisAccount': '', 'exampleType': 'sentence', 'rating': 1, 'url': 'https://www.nytimes.com/2025/05/28/opinion/trump-danger-normalization-shock.html', 'text': 'In a show that recently opened at the LaMaMa Experimental Theater Club in the East Village, a group of actors led by a young, ambitious, charmingly naïve director are almost finished rehearsing Chekhov’s “The Seagull” at the famed Moscow Art Theater when Russia invades Ukraine.', 'frd_rating': 1, 'word': 'naïve', 'labels': [], 'fileId': ''}

    self.assertEqual(sentence_obj, expected_sentence_obj,
                     'Sentence object properties are correct.')

  def test_prefilled_meta(self):
    meta = {'documentTitle': None, 'documentId': 'https://www.nytimes.com/2025/05/28/opinion/trump-danger-normalization-shock.html', 'description': None, 'subjects': [], 'pubDate': '2025-05-28', 'author': 'J. Doe'}

    sentence_obj = fill_out_sentence_object(
        word = "naïve",
        sentence = "In a show that recently opened at the LaMaMa Experimental Theater Club in the East Village, a group of actors led by a young, ambitious, charmingly naïve director are almost finished rehearsing Chekhov’s “The Seagull” at the famed Moscow Art Theater when Russia invades Ukraine.", 
        article_url = "https://www.nytimes.com/2025/05/28/opinion/trump-danger-normalization-shock.html",
        date = "2025-05-28",
        meta = meta,
        api = "nyt"
    )

    del sentence_obj['exampleId']
    expected_sentence_obj = {'metadata': {'searchAPI': 'nyt', 'documentTitle': None, 'crawlDate': '2025-05-28', 'documentId': 'https://www.nytimes.com/2025/05/28/opinion/trump-danger-normalization-shock.html', 'description': None, 'source': 'https://www.nytimes.com/2025/05/28/opinion/trump-danger-normalization-shock.html', 'DOI': None, 'subjects': []}, 'pubDate': '2025-05-28', 'author': 'J. Doe', 'hypothesisAccount': '', 'exampleType': 'sentence', 'rating': 1, 'url': 'https://www.nytimes.com/2025/05/28/opinion/trump-danger-normalization-shock.html', 'text': 'In a show that recently opened at the LaMaMa Experimental Theater Club in the East Village, a group of actors led by a young, ambitious, charmingly naïve director are almost finished rehearsing Chekhov’s “The Seagull” at the famed Moscow Art Theater when Russia invades Ukraine.', 'frd_rating': 1, 'word': 'naïve', 'labels': [], 'fileId': ''}

    self.assertEqual(sentence_obj, expected_sentence_obj,
                     'Sentence object properties are correct.')

if __name__ == '__main__':
    unittest.main()
