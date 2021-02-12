import unittest
from argparse import Namespace

from selenium.webdriver.chrome.webdriver import WebDriver

from bfetch.modules.browser_init import initialise_driver

class TestBrowser(unittest.TestCase):
    def test_browser_init(self):
        """
        Tests that the browser starts properly.
        """
        browser = initialise_driver(show=False)
        self.assertEqual(type(browser), WebDriver)


if __name__ == "__main__":
    unittest.main()
