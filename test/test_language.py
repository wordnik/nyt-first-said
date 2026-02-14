import unittest
from utils.language import is_english

class LanguageSuite(unittest.TestCase):
  def test_basic(self):
      self.assertEqual(is_english("Organizaciones como Poder en Acción, Organized Power in Numbers y 50501 llevan mucho tiempo abogando por las comunidades y los trabajadores migrantes."), False)
      self.assertEqual(is_english("Reserves; 16 Leonel Oviedo, 17 Sef Fa’agase, 18 Misinale Epenisa, 19 Darcy Swain, 20 Will Harris, 21 Henry Robertson, 22 Max Burey, 23 Kurtley Beale."), False)
      self.assertEqual(is_english("In partnership with different agencies, the GEA-8 will introduce solar plants on stilts, agrisolar and solar facilities on canals."), True)
      self.assertEqual(is_english("He then gets to work slicing and portioning fish and making sauces and oils for the aguachiles, sashimis and, yes, ceviches on his menu, setting up his immaculate workstation behind the restaurant’s central marble bar."), True)
      self.assertEqual(is_english("“ODM haiwezi kufa ndo inaanza sasa; ODM ni chama amabaye inawafuasi wengi katika nchi hii ya Kenya, ni chama ya wananchi,” Junet stated."), False)
      self.assertEqual(is_english("Akkada producer ki haretattack … Ikkada seats lo headacck … One more disaster anudeep and viswaksen #FunkyReview #Funky #FunkyMovieReview #Viswaksen #Anudeep Can't call this comedy."), True)
      self.assertEqual(is_english("Bon appétit!"), False)
      self.assertEqual(is_english("It’s not unusual to find yourself cruising down some perfectly groomed run that terminates at a lively après ski bar in some postcard-pretty village, the name and location of which you have absolutely no idea."), True)
      self.assertEqual(is_english("The four Shobha Yatras will converge at Sri Khuralgarh Sahib, regarded as the revered tap asthan of Guru ji."), True)
      self.assertEqual(is_english("Lip kuda synk avvatledu."), False)
      self.assertEqual(is_english("Certainly, it cannot be “babakhe” since he mentioned that his first wife, MaCele, already called him that."), True)
      self.assertEqual(is_english("On the stereo, they are playing atmospheric medieval-style music - “bardcore is one of the genres we’re going for” - says WIlkinson."), True)
      self.assertEqual(is_english("According to reports, citing voice recordings, an individual claiming links to the Bishnoi Gang is allegedly heard warning, “Baat se mukarne ki saza kya hoti hai tujhe bataenge,” suggesting there would be consequences for going back on one’s word."), True)
      self.assertEqual(is_english("It assessed the cost-effectiveness of the shorter bedaquiline-based regimens - BPaL (bedaquiline, pretomanid and linezolid) and BPaLM (with moxifloxacin) - in comparison with the nine-to-11-month and the 18-to 20-month-long bedaquiline-containing treatment plans used under the National TB Elimination Programme (NTEP)."), True)
      self.assertEqual(is_english("Maski mga ganitong activity tamang bihis pa rin kami [Combat shoes are part of our uniform."), False)
      self.assertEqual(is_english("Lydia Begoña Horndler Gil is a profesor en inmunología y biología del cáncer at Universidad San Jorge."), False)


if __name__ == '__main__':
    unittest.main()
