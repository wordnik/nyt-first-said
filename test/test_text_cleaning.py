import unittest
from utils.text_cleaning import remove_punctuation, remove_trouble_characters, has_username, prepare_text_for_textblob

class TestCleaningSuite(unittest.TestCase):
    def test_punctuation(self):
        self.assertEqual(remove_punctuation("Joe’s"), "Joe", "Special apostrophe removed.")

    def test_clean_trouble_chars(self):
        self.maxDiff = None
        self.assertEqual(remove_trouble_characters("\u200Dhas\u200D"), " has ", "Zero-width joiner removed.")
        self.assertEqual(remove_trouble_characters("to\u00A0"), "to ", "Non-breaking space removed.")
        self.assertEqual(remove_trouble_characters(
            "The stores earmarked for \xe2\x80\x8bclosure from February 2 include one in suburban Shanghai, another in Guangzhou, and \xe2\x81\xa0several more in second-tier Chinese cities such as Nantong, Xuzhou and Harbin, IKEA said in a post on its official WeChat account."
        ),
                         "The stores earmarked for closure from February 2 include one in suburban Shanghai, another in Guangzhou, and several more in second-tier Chinese cities such as Nantong, Xuzhou and Harbin, IKEA said in a post on its official WeChat account.",
                         "Non-breaking space removed.")
        self.assertEqual(remove_trouble_characters("The 43-year-old defendant, Davidâ�¯Feeney fromâ�¯Ballymeeney, Dromore West,â�¯Co Sligo, had previously pleaded guilty to being intoxicated, engaging in threatening,â�¯abusiveâ�¯and insulting words or behavior and to assault causing harm to a female garda at the national ploughing championshipsâ�¯at Ratheniska on 21 August 2023."),
        "The 43-year-old defendant, Davidâ Feeney fromâ Ballymeeney, Dromore West,â Co Sligo, had previously pleaded guilty to being intoxicated, engaging in threatening,â abusiveâ and insulting words or behavior and to assault causing harm to a female garda at the national ploughing championshipsâ at Ratheniska on 21 August 2023.")

        self.assertEqual(remove_trouble_characters("I would say to them, accountability…anything that I did, I took responsibility for."), "I would say to them, accountability…anything that I did, I took responsibility for.", "Should not remove ellipsis.") 

    def test_markup(self):
        self.maxDiff = None
        self.assertEqual(remove_trouble_characters("𝗱𝗼𝗻'𝘁 be evil"), "' be evil", "Characters from the High Surrogates Plane removed.")
        self.assertEqual(remove_trouble_characters("Cansino missed two crucial chances late-first a layup"), "Cansino missed two crucial chances late-first a layup", "Hyphen left alone.")

    def test_has_username(self):
        self.assertEqual(has_username("@ausmencricket"), True, "@-based username found.")
        self.assertEqual(has_username("cricket"), False, "Normal word identified.")
        self.assertEqual(has_username("ab@normal.com"), True, "Email found.")

    def test_parse_prep(self):
        self.maxDiff = None
        self.assertEqual(prepare_text_for_textblob("Cansino missed two crucial chances late—first a layup"), "Cansino missed two crucial chances late — first a layup", "Emdash replaced")
        self.assertEqual(prepare_text_for_textblob("election‑ready"), "election-ready", "Nonbreaking hyphen replaced")
        self.assertEqual(prepare_text_for_textblob("very angry'﻿"), "very angry'", "Removed zero-width nonbreaking space.")

if __name__ == '__main__':
    unittest.main()
