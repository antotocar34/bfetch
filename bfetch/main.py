import os
import sys
import time
import re
import csv
import logging
import argparse as arg
from typing import List, Tuple

from pathlib import Path

from selenium.common.exceptions import (
    InvalidArgumentException,
    UnexpectedAlertPresentException,
)
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from bs4.element import Tag

import modules.config as g
from modules.filehandler import sort_to_folder_from_tree
from modules.browser_init import initialise_driver
from modules.button_finder import find_and_click_button
from modules.interactions import log_in
from modules.utils import get_request, make_soup, normalize_name, make_wfu

from modules.html_parser import (
    find_links,
    get_content_tags,
    get_module_tags,
)

from modules.filetree import FileTree, Node, File, load_tree_from_file

def arguments() -> Tuple[bool, float]:
    parser = arg.ArgumentParser(description="Download files from blackboard")
    fast = 1.5
    slow = 0.1
    default = 0.8
    parser.add_argument("-s", "--show", default=False, action="store_true",
                        help="Whether to show the browser.")
    parser.add_argument(
        "-S", "--slow", action="store_const", default=None, const=slow,
        help="Dowloads files at a slower sleep"
    )
    parser.add_argument(
        "-F", "--fast", action="store_const", default=None, const=fast,
        help="Downloads the files as fast as possible."
    )
    args = parser.parse_args()

    if args.slow:
        speed = args.slow
    elif args.fast:
        speed = args.fast
    else:
        speed = default
    
    return args.show, speed

def init_tree() -> FileTree:
    """
    Initialise Tree
    """
    tree = FileTree()
    root = Node(File("root", "", "root"))
    tree.insert(root)
    return tree



# Initialise the log file
log_file = g.DATA_DIR + "/selenium_blackboard.log"
logging.basicConfig(filename=log_file, level=logging.INFO, filemode="w")


def follow_node(browser: WebDriver, node: Node) -> None:
    """
    Get request the URL and adds the node to the tree.
    """
    TREE.insert(node, TREE.pointer)
    get_request(browser, node.file.url)


def tag_to_node(tag: Tag, kind: str) -> Node:
    name = normalize_name(tag.text)
    url = make_wfu(str(tag["href"]))
    file_obj = File(name, url, kind)
    return Node(file_obj)



def download_file(browser: WebDriver, node: Node) -> None:
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

        # file_path: Path
        _, file_path = max(files)

    node.file.file_name = file_path.name
    node.file.completed = True
    print(f"DOWNLOADED : {node.file.file_name}")



def files_folders(browser: WebDriver):
    # Might be a bit slow
    pdf_link_tags, folders = find_links(browser)

    for tag in pdf_link_tags:

        file_node = tag_to_node(tag, "file")
        # This is where the new pointer is attached.
        # download_file(browser, file_node)

        TREE.insert(file_node, TREE.pointer)

        # Mark the file as have been downloaded
        # Attach back to section node.
        TREE.attach_pointer(file_node.parent)

    for tag in folders:

        folder_node = tag_to_node(tag, "section")

        follow_node(browser, folder_node)

        files_folders(browser)

        folder_node.file.completed = True

        print(folder_node.name + " inserted")
        TREE.attach_pointer(folder_node.parent)


def first_section(browser):
    try:
        content_tags = get_content_tags(browser)
    except AssertionError:
        print("found no content tags.")
        return
    for tag in content_tags:

        panel_node = tag_to_node(tag, "section")

        follow_node(browser, panel_node)
        files_folders(browser)

        panel_node.file.completed = True
        # Attach back to module
        TREE.attach_pointer(panel_node.parent)

    return


def make_tree(browser: WebDriver, module_tags: List[Tag]):
    """
    Main Function of the program.
    Recursively goes through blackboard file structure.
    """
    for tag in module_tags[:2]:

        module_node = tag_to_node(tag, "module")

        # Get request to module_node.file.url
        follow_node(browser, module_node)
        first_section(browser)

        module_node.file.completed = True

        # TODO change this
        assert TREE.root == module_node.parent
        TREE.attach_pointer(module_node.parent)



def download_file_nodes(browser: WebDriver , tree: FileTree) -> None:
    """
    Goes through the tree and downloads nodes that have not been downloaded.
    """
    file_nodes = [ n
                   for n in tree.nodes
                   if n.file.kind == "file" and n.file.completed == False ]

    for n in file_nodes:
        download_file(browser, n)
    return None


def run_program():

    show, speed = arguments()

    SPEED = speed

    browser = initialise_driver(show)

    log_in(browser)

    # Click the Module List
    find_and_click_button(
        browser, xpath="""//*[@id="Module List"]/a""", id_string="Module List"
    )
    # DO NOT REMOVE
    time.sleep(1)

    module_tags = get_module_tags(browser)

    make_tree(browser, module_tags)

    download_file_nodes(browser, TREE) 

    browser.quit()

try:
    tree_path = f"{g.DATA_DIR}/noinuse.json"
    TREE = load_tree_from_file(tree_path)
except FileNotFoundError:
    TREE = init_tree()

def main():
    try:
        run_program()
    except InvalidArgumentException:
        input("Close the previous browser window and then press enter.")
        run_program()
    finally:
        TREE.write_to_file()
        sort_to_folder_from_tree(TREE)

        downloaded = [n for n in TREE.nodes if n.file.kind == 'file' and n.file.completed == True]
        print(
            f"\n\nTotal downloaded: {len(downloaded)}"
        )

if __name__ == "__main__":
    main()
