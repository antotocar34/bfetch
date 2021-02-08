import os
import sys
import time
import re
import csv
import logging
from pathlib import Path

from selenium.common.exceptions import (
    InvalidArgumentException,
    UnexpectedAlertPresentException,
)
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from bs4.element import Tag

import modules.config as g
from modules.filehandler import sort_to_folder_from_tree
from modules.browser_init import initialise_driver
from modules.button_finder import find_and_click_button
from modules.interactions import log_in
from modules.arguments import parse_args
from modules.utils import get_request, make_soup, normalize_name, make_wfu

from modules.html_parser import (
    find_pdf_links,
    get_content_tags,
    get_module_tags,
)

from modules.general_tree import FileTree, Node, File


def init_tree() -> FileTree:
    """
    Initialise Tree
    """
    tree = FileTree()
    root = Node(File("root", "", "root"))
    tree.insert(root)
    return tree


# TODO move this
TREE = init_tree()

# TODO implement speed
# DEFAULT SPEED
SPEED = g.SPEED

args = parse_args()

if args.S:
    SPEED = args.S
if args.F:
    SPEED = args.F


# Initialise the log file
log_file = g.DATA_DIR + "/selenium_blackboard.log"
logging.basicConfig(filename=log_file, level=logging.INFO, filemode="w")


def follow_node(browser, node) -> None:
    """
    Get request the URL and adds the node to the tree.
    """
    TREE.insert(node, TREE.pointer)
    get_request(browser, node.file.url)


def tag_to_node(tag, kind: str) -> Node:
    name = normalize_name(tag.text)
    url = make_wfu(str(tag["href"]))
    file_obj = File(name, url, kind)
    return Node(file_obj)



def download_file(browser, node: Node) -> None:
    """
    Downloads file_node.
    """

    get_request(browser, node.file.url)

    dl_dir = Path(g.DOWNLOAD_PATH)

    # Wait for download to finish.
    file_path = None
    while not file_path or "crdownload" in file_path.suffix:
        try:
            files = [(f.stat().st_mtime, f) for f in dl_dir.iterdir()]
        except FileNotFoundError:  # In case file completes
            # while `files` is being evaluated.
            continue

        _, file_path = max(files)

    node.file.file_name = file_path.name
    node.file.completed = True
    print(f"DOWNLOADED : {node.file.file_name}")

    TREE.insert(node, TREE.pointer)


def files_folders(browser):
    pdf_link_tags, folders = find_pdf_links(browser)

    for tag in pdf_link_tags:

        file_node = tag_to_node(tag, "file")

        banned_strings = [
            "turnitin",
            "launchAssessment",
            "mailto",
            "docs.google.com",
            "youtube",
            "tcdlibrary",
            "#",
        ]

        check_banned = all(
            [s not in file_node.file.url for s in banned_strings]
        )

        if check_banned:
            # This is where the new pointer is attached.
            download_file(browser, file_node)

            # Mark the file as have been downloaded
            # Attach back to section node.
            TREE.attach_pointer(file_node.parent)

    for tag in folders:

        folder_node = tag_to_node(tag, "section")

        follow_node(browser, folder_node)

        files_folders(browser)

        folder_node.file.completed = True

        TREE.attach_pointer(folder_node.parent)


def first_section(browser):
    content_tags = get_content_tags(browser)
    for tag in content_tags:

        panel_node = tag_to_node(tag, "section")

        follow_node(browser, panel_node)
        files_folders(browser)

        panel_node.file.completed = True
        # Attach back to module
        TREE.attach_pointer(panel_node.parent)

    return


def make_tree(browser, module_tags):
    """
    Main Function of the program.
    """
    for tag in module_tags:

        module_node = tag_to_node(tag, "module")

        # Get request to module_node.file.url
        follow_node(browser, module_node)
        first_section(browser)

        module_node.file.completed = True
        # TODO change this
        assert TREE.root == module_node.parent
        TREE.attach_pointer(module_node.parent)


def main():

    browser = initialise_driver(args)

    log_in(browser)

    # Click the Module List
    find_and_click_button(
        browser, xpath="""//*[@id="Module List"]/a""", id_string="Module List"
    )

    time.sleep(1)  # TODO write a smart wait function.
    module_tags = get_module_tags(browser)

    make_tree(browser, module_tags)

    browser.quit()


if __name__ == "__main__":
    # TODO rename contents
    # CONTENTS = read_from_file()
    CONTENTS = ""

    logging.info(CONTENTS)
    try:
        main()
    except InvalidArgumentException:
        input("Close the previous browser window and then press enter.")
        main()
    finally:
        TREE.write_to_file()
        sort_to_folder_from_tree(TREE)

        downloaded = [n for n in TREE.nodes if n.file.kind == 'file' and n.file.completed == True]
        print(
            f"\n\nTotal downloaded: {len(downloaded)}"
        )

# TODO decorator to handle node repointering?