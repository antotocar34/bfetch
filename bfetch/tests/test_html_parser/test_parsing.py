import unittest
from argparse import Namespace

from selenium.webdriver.chrome.webdriver import WebDriver
from bs4 import BeautifulSoup

import bfetch.modules.config as g
from bfetch.modules.html_parser import link_aggregator

def get_test_file():
    file_path = g.PROJ_DIR + '/bfetch/tests/files/files_and_folder.html'
    with open(file_path, 'r') as f:
        html = f.read()
        return html

class TestBrowser(unittest.TestCase):

    def test_file_folder_parsing(self):

        html = get_test_file()
        soup = BeautifulSoup(html, 'html.parser')
        files, folders = link_aggregator(soup)
        files = {f.text for f in files}
        folders = {f.text.strip() for f in folders}

        g_files = {"Syllabus & Introduction", "Reading List", "Slides - Introduction"}
        g_folders = {"Readings"}

        print(f"\nOUTPUT: {files}", f"\nEXPECTED:{g_files}")
        print(f"\nOUTPUT: {folders}", f"\nEXPECTED:{g_folders}")

        self.assertTrue(set(files) == g_files and set(folders) == g_folders)
        

    def test_section_parsing(self):
        pass

if __name__ == "__main__":
    unittest.main()
