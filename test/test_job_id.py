import unittest
from datetime import date
from parsers.utils import get_job_filename

class JobNameSuite(unittest.TestCase):
  def test_basic(self):
    sentence_obj_json = '{"metadata": {"searchAPI": "nyt", "documentTitle": null, "crawlDate": "2025-05-28", "documentId": null, "description": null, "source": "https://www.nytimes.com/2025/05/28/opinion/trump-danger-normalization-shock.html", "DOI": null, "subjects": null}, "pubDate": null, "author": null, "hypothesisAccount": "", "exampleType": "", "rating": 1, "url": "https://www.nytimes.com/2025/05/28/opinion/trump-danger-normalization-shock.html", "text": "In a show that recently opened at the LaMaMa Experimental Theater Club in the East Village, a group of actors led by a young, ambitious, charmingly na\u00efve director are almost finished rehearsing Chekhov\u2019s \u201cThe Seagull\u201d at the famed Moscow Art Theater when Russia invades Ukraine.", "frd_rating": 1, "exampleId": "fee29452-100e-4d30-a5a7-bc4a8db3bbb4", "word": "na\u00efve", "labels": [], "fileId": ""}'
    
    job_filename = get_job_filename(sentence_obj_json, date.fromisoformat("2025-05-28"), "naïve")

    self.assertEqual(job_filename, "orDZAtKxcRYTynZCoTYQB2eaHUA=_2025-05-28_naïve.json",
                     "job_filename is correct")

if __name__ == '__main__':
    unittest.main()
