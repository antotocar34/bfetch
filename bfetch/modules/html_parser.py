import logging
import re
from typing import Tuple, List, Optional
from bs4.element import Tag

try:
    from utils import make_soup
except:
    from modules.utils import make_soup


def get_content_tags(browser):
    """
    TODO WRITE MULTIPLE WAYS OF DOING IT
    """
    soup = make_soup(browser)
    content_tags = soup.find("div", {"class": "navPaletteContent"}).find_all(
        "a"
    )
    return content_tags


def get_module_tags(browser):
    """
    Get's <a> tags according to
    module name regex.

    browser -> [module_tag]
    """
    regex_for_module_names = "^[A-Z]{2,3}[0-9A-Z]{3,5}.*"
    soup = make_soup(browser)
    tags = soup.find_all("a")
    module_tags = []
    for tag in tags:
        if re.search(regex_for_module_names, str(tag.text)) is not None:
            module_tags.append(tag)
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
) -> Optional[List[str]]:
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




def find_pdf_links(browser) -> Tuple[List[Tag], List[Tag]]:
    """
    Find the appropriate link tags according to certain features of
    the links themselves, and recognize folders. Make a list of
    those anchor tags, while taking out the folder links.
    """
    # This function contains the logic to find pdf links.

    soup = make_soup(browser)

    # Anyway to generalise this code, so that is it easy to
    # search for many types of links?
    # Search div with attached files.
    regex_for_pdf_links_1 = re.compile("^contentListItem:.*")
    pdf_link_tags_1 = [
        x.find("a") for x in soup.find_all("li", {"id": regex_for_pdf_links_1})
    ]
    pdf_link_tags_2 = [
        x.find("a")
        for x in soup.find_all("ul", {"class": "attachments clearfix"})
    ]
    # List of all possibly interesting items.
    pdf_link_tags = pdf_link_tags_1 + pdf_link_tags_2
    # Filter out None.
    pdf_link_tags = [tag for tag in pdf_link_tags if tag is not None]
    try:
        logging.info([pdf.text for pdf in pdf_link_tags])
    except AttributeError:
        pass

    # Remove any non tag from list.
    pdf_link_tags = [tag for tag in pdf_link_tags if type(tag) is Tag]

    # Recognize folder based on href
    folders = [
        tag for tag in pdf_link_tags if "listContent" in str(tag["href"])
    ]

    # remove folder from links
    pdf_link_tags = list(set(pdf_link_tags) - set(folders))

    # TODO remove hrefs that have 'turnitin' in them.

    return pdf_link_tags, folders
