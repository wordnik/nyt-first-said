import unittest
from utils.headless import HeadlessBrowser

class HeadlessSuite(unittest.TestCase):
  def test_basic(self):
      browser = HeadlessBrowser()
      page = browser.get_page("https://wordnik.com/")
      button_element = page.locator("input[name='commit']")
      self.assertTrue(button_element, "Search button is found on the page.")
      print(button_element.get_attribute("value"))
      self.assertEqual(button_element.get_attribute("value"), "I always feel lucky", "We found the button with the correct value.")
      browser.close()
      with self.assertRaisesRegex(ChildProcessError, 'Browser not initialized'):
          browser.get_page("https://google.com")

if __name__ == '__main__':
    unittest.main()
