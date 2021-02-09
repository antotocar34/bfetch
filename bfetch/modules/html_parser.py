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
def get_content_tags(browser: WebDriver) -> List[Tag]:
    """
    TODO WRITE MULTIPLE WAYS OF DOING IT
    """
    soup = make_soup(browser)
    content_tags = soup.find("div", {"class": "navPaletteContent"}).find_all(
        "a"
    )
    assert content_tags != []
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


# def return_filtered_tags(tags: List[Tag]) -> List[Tag]:
#     """
#     Filters out tags according to filter_out_noise function.
#     """
#     regex_for_module_names = '^[A-Z]{2,3}[0-9A-Z]{3,5}.*'
#      # In case I did something wrong.
#     old_regex_for_module_names = '^[A-Z]{3}[0-9]{5}-[A-Z]-[A-Z0-9]*.*$'

#     for tag in tags.copy():
#         if filter_out_noise(tag, regex) is True:
#             tags.remove(tag)
#     return tags

# def filter_out_noise(tag, regex):
#     """
#     Filter out None, Announcements and whatever matches regex.
#     """
#     if tag.string is None:
#         return True
#     elif tag.string == "Announcements":
#         logging.info("Skipped Announcements")
#         return True
#     elif re.search(re.compile(regex), tag.string) is not None:
#         return True
#     else:
#         return False

def match_regex_list(
    regex: str, things_to_match: List[str]
) -> List[re.Match[str]]:
    """
    Checks if strings in things_to_match matches the
    regular expression, if not fileter them out.
    """
    pattern = re.compile(regex)
    matched = []
    for thing in things_to_match:
        match = pattern.match(str(thing))
        if match is not None:
            matched.append(match)
    return matched


def link_aggregator(soup: BeautifulSoup) -> List[Tag]:
    """
    Finds links at the section level.
    """
    regex1 = re.compile("^contentListItem:.*")

    links: List[List[Tag]]
    links = [
    # Find folders
    [t.find("a") 
     for t in soup.find_all("li", {"id": regex1})],
    # Not sure
    [t.find("a") 
     for t in soup.find_all("ul", {"class": "attachments clearfix"})],
    # General finder, designed to match this kind of link.
    # https://tcd.blackboard.com/bbcswebdav/pid-1271258-dt-content-rid-7326038_1/xid-7326038_1
    [t.find("a")
     for t in soup.find_all() 
     if "pid" in t.get("href") and "xid" in t.get("href")
     ],
            ]

    # flatten links
    tags = [t for tags in links for t in tags]

    filtered_tags = [tag for tag in tags if filter_function(tag) == True]
    return filtered_tags

def filter_function(tag: Tag) -> bool:
    functions = [
            lambda t: type(t) is Tag, 
            lambda t: t.get("href") is not None
            ]
    application = [f(tag) for f in functions]
    return all(application)
     


def find_links(browser: WebDriver) -> Tuple[List[Tag], List[Tag]]:
    """
    Find the appropriate link tags according to certain features of
    the links themselves, and recognize folders. Make a list of
    those anchor tags, while taking out the folder links.
    """
    # This function contains the logic to find pdf links.

    soup = make_soup(browser)


    found_tags = link_aggregator(soup)

    # Anyway to generalise this code, so that is it easy to
    # search for many types of links?
    # Search div with attached files.

    # Remove any non tag from list.

    # Recognize folder based on href
    folders = [
        tag for tag in found_tags if "listContent" in str(tag["href"])
    ]

    # remove folder from links
    pdf_link_tags = list(set(found_tags) - set(folders))

    # TODO remove hrefs that have 'turnitin' in them.

    return pdf_link_tags, folders
