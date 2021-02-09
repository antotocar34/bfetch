from typing import Type
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver
# from modules.filetree import Node, File, FileTree


def get_request(browser: WebDriver, url: str) -> BeautifulSoup:
    """
    Goes to to the designated url and
    returns a beautiful soup object.
    """
    # print(f"get_request: {url}")
    browser.get(url)
    soup = make_soup(browser)
    return soup

def make_soup(browser: WebDriver):
    """Returns a beautiful soup object of the current url."""
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def normalize_name(string: str) -> str:
    """
    Lecture Slides -> lecture_slides
    """
    if string != "":
        return string.replace(" ", "_").lower().strip()
    else:
        return "no_name_defined"

def make_wfu(url_part: str, url_base: str ='https://tcd.blackboard.com') -> str:
    """
    Checks to see if root address is in the url, if not
    append it.
    """
    # Strip url_part of all whitespace

    if not url_part.startswith("http") and url_base not in url_part:
        return url_base + url_part.strip()
    else:
        return url_part
