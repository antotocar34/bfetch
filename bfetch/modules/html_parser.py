import logging
import re
from typing import Tuple, List, Optional, Any
from selenium.webdriver.chrome.webdriver import WebDriver
from bs4.element import Tag
from bs4 import BeautifulSoup

from modules.utils import make_soup


# TODO Make sure this does not happend again.
#
# File "/home/carneca/Documents/Python/automation/bfetch/bfetch/modules/html_parser.py", line 15, in get_content_tags
#     content_tags = soup.find("div", {"class": "navPaletteContent"}).find_all(
# AttributeError: 'NoneType' object has no attribute 'find_all'
#
def filter_content_tags(content_tags: List[Tag],
                        browser: WebDriver
                        ) -> List[Tag]:
    content_tags = [t for t in content_tags if t is not None]
    content_tags = [t 
                    for t in content_tags 
                    if t.text != "Announcements" and t.href != browser.current_url]
    return content_tags

def get_content_tags(browser: WebDriver) -> List[Tag]:
    """
    TODO WRITE MULTIPLE WAYS OF DOING IT
    """
    soup = make_soup(browser)
    content_tags = soup.find("div", {"class": "navPaletteContent"}).find_all(
        "a"
    )
    assert content_tags != []

    content_tags = filter_content_tags(content_tags, browser)

    return content_tags


def get_module_tags(browser: WebDriver) -> List[Tag]:
    """
    Get's <a> tags according to
    module name regex.
    """
    regex_for_module_names = "^[A-Z]{2,3}[0-9A-Z]{3,5}.*"
    soup = make_soup(browser)
    tags = soup.find_all("a")
    module_tags = []
    for tag in tags:
        if re.search(regex_for_module_names, str(tag.text)) is not None:
            module_tags.append(tag)
    assert module_tags != [], "Did not find any module tags."
    return module_tags


def filter_function(tag: Tag) -> bool:
    """
    Tests that tags are valid.
    """
    functions = [
            lambda t: type(t) is Tag, 
            lambda t: bool(t.get("href"))
            ]
    application: List[bool] = [f(tag) for f in functions]
    return all(application)
     

def general_file_link_getter(soup: BeautifulSoup) -> List[Tag]:
    """
    # General finder, designed to match this kind of link.
    /bbcswebdav/pid-1271258-dt-content-rid-7326038_1/xid-7326038_1

    # Will also get request links that end in a common document formar
    """
    all_tags: List[Tag] = [t for t in soup.find_all("a") if t is not None]

    tags = [t for t in all_tags if t.get("href") is not None]

    regex = re.compile(r"(pid-\d+|xid-\d+)|(\.(pdf|\.pptx|\.docx|\.odt)$)")

    general_link_tags = [t for t in tags 
                         if bool(re.search(regex, str(t["href"])))
                        ]
    return general_link_tags

def folder_link_getter(soup: BeautifulSoup) -> List[Tag]:
    """
    # General finder, designed to match this kind of link.
    /bbcswebdav/pid-1271258-dt-content-rid-7326038_1/xid-7326038_1

    # Will also get request links that end in a common document formar
    """
    # TODO find a more robust way of parsing folders.
    regex_for_folders = re.compile(r"^contentListItem:.*") 
    all_tags: List[Tag] = [t.find("a") 
                           for t 
                           in soup.find_all("li", {"id": regex_for_folders})]

    no_none_tags = [t for t in all_tags if t is not None]
    tags = [t for t in no_none_tags if t.get("href") is not None
                                    and not t.get("href").endswith("#")]

    # this is not going to do.
    regex = re.compile(r"listContent")
    folder_tags = [t for t in tags 
                         if bool(re.search(regex, str(t["href"])))
                        ]
    return folder_tags

def link_aggregator(soup: BeautifulSoup) -> Tuple[List[Tag], List[Tag]]:
    """
    Finds links at the section level.
    """

    folder_links = folder_link_getter(soup)
    folder_links = [t for t in folder_links if filter_function(t)]

    general_links = general_file_link_getter(soup)
    general_links = [t for t in general_links if filter_function(t)]

    return general_links, folder_links




def find_links(browser: WebDriver) -> Tuple[List[Tag], List[Tag]]:
    """
    Find the appropriate link tags according to certain features of
    the links themselves, and recognize folders. Make a list of
    those anchor tags, while taking out the folder links.
    """

    soup = make_soup(browser)


    pdf_link_tags, folder_tags = link_aggregator(soup)

    return pdf_link_tags, folder_tags
