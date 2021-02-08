import os
import sys
import argparse as arg
import time
import re
import csv
import logging

from selenium.common.exceptions import (
    InvalidArgumentException,
    UnexpectedAlertPresentException,
)

from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

import modules.config as g
from modules.utils import get_request, make_soup, normalize_name
from modules.browser_init import initialise_driver
from modules.button_finder import find_and_click_button
from modules.interactions import log_in
from modules.html_parser import find_pdf_links, get_content_tags

from modules.general_tree import FileTree, Node, File

def init_tree():
    tree = FileTree()
    root = Node(File("root", "", "root"))
    print(root.node_type)
    tree.insert(root)
    return tree

TREE = init_tree()

# TODO refactor this into it's own thing
def parse_args():
    """Parses Argument given"""
    parser = arg.ArgumentParser(description="Download files from blackboard")
    fast = 1.5
    slow = 0.1
    default = 0.8
    parser.add_argument("-s", "--show", action="store_false")
    parser.add_argument("-S", action="store_const", default=default, const=fast)
    parser.add_argument("-F", action="store_const", default=default, const=slow)
    args = parser.parse_args()
    return args


SPEED = g.SPEED

args = parse_args()

if args.S:
    SPEED = args.S
if args.F:
    SPEED = args.F


# Initialise the log file
log_file = g.DATA_DIR + "/selenium_blackboard.log"
logging.basicConfig(filename=log_file, level=logging.INFO, filemode="w")

def tag_to_file_object(tag, kind):
    name = normalize_name(tag.text)
    url = make_wfu(str(tag['href']))
    return File(name, url, kind)


def go_through_modules(browser, module_tags):
    """
    Iterate through the tags that lead to modules and call
    the go_through_side_panel function on each of them.
    """
    # This function does not need to be refactored.
    for tag in module_tags:

        f_obj = tag_to_file_object(tag, "module")
        module_name = f_obj.name
        url = f_obj.url


        module_node = Node(f_obj)
        TREE.insert(module_node, TREE["root"])

        soup = get_request(browser, url)
        # if speed != 0.1:
        time.sleep(SPEED / 2)

        go_through_side_panel(browser, soup, module_name)


def go_through_side_panel(browser, soup, module_name):
    """
    Open the sidebar menu and find all the appropriate links in that menu.
    Follow those links and call the go_through_pdf_links on those pages.
    """

    # Gets the <a> tags in the sidebar
    content_tags = get_content_tags(soup)

    for tag in content_tags:

        f_obj = tag_to_file_object(tag, "module")
        section_name = f_obj.name
        url = f_obj.url

        mnode = TREE[module_name]
        section_node = Node(File(section_name, url, "section"))
        TREE.insert(section_node, mnode)

        try:
            soup = get_request(browser, url)
        except UnexpectedAlertPresentException:
            breakpoint()

        time.sleep(SPEED / 2)
        # Implement a function to create this directory later.
        go_through_pdf_links(
            browser, soup, module_name, section_name
        )  # Add , directory_name argument


# TODO write a function that takes the download path and
#      creates a new directory according to sub names.
def go_through_pdf_links(
    browser, soup, module_name, section_name, folder_names=[]
):  # Add , directory_name argument
    """
    Call find_pdf_links and iterate through those links using
    well formatted links. Filter those links that have
    'turnitin' in them and those links that have already
    been downloaded from.

    If there are folders, call this function recursively on
    those folders.
    """
    pdf_link_tags, folders = find_pdf_links(browser, soup)

    for tag in pdf_link_tags:

        f_obj = tag_to_file_object(tag, "file")
        url = f_obj.url

        # Check for specific strings to avoid in url.
        # Should I go for more of a duck typing approach here?
        # TODO there should not be banned strings there should only be allowed string
        banned_strings = [
            "turnitin",
            "launchAssessment",
            "mailto",
            # Forms
            "docs.google.com",
            # TODO add youtube-dl support?
            # TODO oh yeah this shit is fucked.
            "youtube",
            "tcdlibrary",
            "#",
        ]

        check_banned = all([s not in url for s in banned_strings])

        if check_banned and tag.text not in CONTENTS:
            # ^-- Could this step be done earlier?
            # Write download function
            # TODO Put an exception block here once you've sorted
            # out the folder stuff.
            # TODO think about putting a big try block here.
            get_request(browser, url)

            filename = f_obj.name

            filename_node = Node(f_obj)
            TREE.insert(filename_node, TREE[section_name])

            write_href_to_file(filename)

            # print(f"downloaded file: {tag.text}")
            time.sleep(SPEED + 1)
            # file_name = tag.text
            try:
                sort_to_folder(
                    module_name, section_name, subfolder=folder_names
                )
            except:
                pass
                # print(
                #     f"The file '{tag.text}' was not downloaded, maybe it was not a file?"
                # )
                # print(f"Include a banned term in url?\nSee url -> {href}")

    # 'if folders:'?
    if folders:
        # if any([type(x) is str for x in folders]):
        #     breakpoint()
        for folder in folders:

            folder_obj = tag_to_file_object(folder, "section")
            url = folder_obj.url
            folder_name = folder_obj.name

            sub_soup = get_request(browser, url)

            if folder_names == []:
                parent_node = TREE[section_name]
            else:
                pass
            folder_node = Node(folder_obj)
            TREE.insert(folder_node, parent_node)

            # Recursively go through folder hierarchy.
            go_through_pdf_links(
                browser, sub_soup, module_name, 
                section_name, folder_names + [folder_name]
            )


def write_href_to_file(string):
    """
    Load list from file with hrefs.
    This function seems to be misnamed.
    It does not write a href but rather the
    name of the file.
    It should probably write the href?
    """
    log_name = g.DATA_DIR + "/downloaded_pdfs.csv"
    with open(log_name, "a") as f:
        file_writer = csv.writer(
            f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        file_writer.writerow([string.rstrip()])
    return


# TODO needs to be renamed and docstring needs to be improved.
def read_from_file():
    """Read from file with filenames"""
    log_name = g.DATA_DIR + "/downloaded_pdfs.csv"
    with open(log_name, "r") as f:
        reader = csv.reader(f, delimiter=",")
        try:
            downloaded = [row[0] for row in reader]
        except IndexError:
            return []
        logging.info(downloaded)
        return downloaded


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


def main():

    browser = initialise_driver(args)

    log_in(browser)

    # Click the Module List
    find_and_click_button(
        browser, xpath="""//*[@id="Module List"]/a""", id_string="Module List"
    )

    time.sleep(1)  # TODO write a smart wait function.
    module_tags = get_module_tags(browser)

    # Loop through module links, collecting all the pdfs
    go_through_modules(browser, module_tags)

    return browser


if __name__ == "__main__":
    # TODO rename contents
    # CONTENTS = read_from_file()
    CONTENTS = ""

    logging.info(CONTENTS)
    try:
        browser = main()
    except InvalidArgumentException:
        input("Close the previous browser window.")
        main()
    finally:
        TREE.write_to_file()
    browser.quit()

# TODO convert tag to Node?
