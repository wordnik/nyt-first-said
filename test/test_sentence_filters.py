import unittest
from utils.sentence_filters import has_balanced_punctuation, contains_line_breaks

class SentenceFiltersSuite(unittest.TestCase):
    def test_punctuation_check(self):
        self.assertEqual(has_balanced_punctuation("So many up and downs, but where there’s a will, there’s a way.”"), False)
        self.assertEqual(has_balanced_punctuation("“So many up and downs, but where there’s a will, there’s a way.”"), True)
        self.assertEqual(has_balanced_punctuation('They said, "OK."'), True)
        self.assertEqual(has_balanced_punctuation('"OK," they said.'), True)
        self.assertEqual(has_balanced_punctuation('"OK, they said.'), False)
        self.assertEqual(has_balanced_punctuation('OK, they" said.'), False)
        self.assertEqual(has_balanced_punctuation('"Supposedly, there were "real" "concerns about this," she said.'), False)

    def test_linebreak_check(self):
        self.assertEqual(contains_line_breaks("artavia lafrance\n That recognition restored something visible by the time the school day ended."), True)
        self.assertEqual(contains_line_breaks("That recognition restored something visible by the time the school day ended."), False)
        self.assertEqual(contains_line_breaks("\n\n \n                \n\n \n\n  See Dorset’s wildlife in a completely new light at a special biofluorescence walk at RSPB Arne."), True)
        self.assertEqual(contains_line_breaks("Revenue climbed 38% year-over-year… Read More\n\n        Read more in: Fintech         |  Tagged bnpl, earnings report, klarna, payments"), True)
        self.assertEqual(contains_line_breaks("Read people's comments below:\nMathonolo felt sorry for the people who were tricked:\n Swidi Lomkhuhlane 💋 felt the victim should have taken better precautions:\n JayCob🇿🇦 agreed that the scam was avoidable:\nRead also\nKid takes over Afrikaans class after misbehaving in TikTok video\n Elizma🇿🇦 felt sorry the young lady and her peers:\nIsabel bontle added:\n Les related to the clip: \nNotification!"), True)
        self.assertEqual(contains_line_breaks("The “bribeumentary” that Jeff Bezos conjured up about his wife was a flop."), False)


if __name__ == '__main__':
    unittest.main()
