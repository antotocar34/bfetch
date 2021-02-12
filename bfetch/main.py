import os
import sys
import time
import re
import csv
import logging
import argparse as arg
from typing import List, Tuple
from json.decoder import JSONDecodeError

from pathlib import Path

from selenium.common.exceptions import (
    InvalidArgumentException,
    UnexpectedAlertPresentException,
)
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from bs4.element import Tag

import bfetch.modules.config as g
from bfetch.modules.arguments import arguments
from bfetch.modules.browser_init import initialise_driver
from bfetch.modules.button_finder import find_and_click_button
from bfetch.modules.interactions import log_in, click_module_list
from bfetch.modules.utils import (
    get_request,
    make_soup,
    normalize_name,
    make_wfu,
)

from bfetch.modules.html_parser import (
    find_links,
    get_content_tags,
    get_module_tags,
)

from bfetch.modules.filehandler import (
    sort_to_folder_from_tree,
    download_file_nodes,
)

from bfetch.modules.downloader import download_nodes

from bfetch.modules.filetree import FileTree, Node, File, load_tree_from_file


def init_tree() -> FileTree:
    """
    Initialise Tree
    """
    tree = FileTree()
    root = Node(File("root", "", "root"))
    tree.insert(root)
    return tree


def follow_node(tree: FileTree, browser: WebDriver, node: Node) -> None:
    """
    Get request the URL and adds the node to the tree.
    """
    tree.insert(node, tree.pointer)
    get_request(browser, node.file.url)


def tag_to_node(tag: Tag, kind: str) -> Node:
    name = normalize_name(tag.text)
    url = make_wfu(str(tag["href"]))
    file_obj = File(name, url, kind)
    return Node(file_obj)


def files_folders(tree: FileTree, browser: WebDriver):
    # Might be a bit slow
    pdf_link_tags, folders = find_links(browser)

    for tag in pdf_link_tags:

        file_node = tag_to_node(tag, "file")

        tree.insert(file_node, tree.pointer)

        # Mark the file as have been downloaded
        # Attach back to section node.
        tree.attach_pointer(file_node.parent)

    for tag in folders:

        folder_node = tag_to_node(tag, "section")

        follow_node(tree, browser, folder_node)

        # Recursively go through called
        files_folders(tree, browser)

        folder_node.file.completed = True

        print(folder_node.name + " inserted")
        tree.attach_pointer(folder_node.parent)


def first_section(tree: FileTree, browser: WebDriver):
    try:
        content_tags = get_content_tags(browser)
    except AssertionError:
        print("found no content tags.")
        content_tags = []
    for tag in content_tags:

        panel_node = tag_to_node(tag, "section")

        follow_node(tree, browser, panel_node)
        files_folders(tree, browser)

        panel_node.file.completed = True
        # Attach back to module
        tree.attach_pointer(panel_node.parent)

    return


def make_tree(tree: FileTree, browser: WebDriver, module_tags: List[Tag]):
    """
    Main Function of the program.
    Recursively goes through blackboard file structure.
    """
    for tag in module_tags[:2]:

        module_node = tag_to_node(tag, "module")

        # Get request to module_node.file.url
        follow_node(tree, browser, module_node)
        first_section(tree, browser)

        module_node.file.completed = True

        assert tree.root == module_node.parent
        tree.attach_pointer(module_node.parent)


def run_program(tree: FileTree):

    show, speed = arguments()

    global SPEED
    SPEED = speed

    browser = initialise_driver(show)

    log_in(browser)

    click_module_list(browser)

    module_tags = get_module_tags(browser)

    make_tree(tree, browser, module_tags)

    download_nodes(browser, tree)

    browser.quit()


def main():
    try:
        tree_path = f"{g.DATA_DIR}/structure.json"
        TREE = load_tree_from_file(tree_path)
    except (FileNotFoundError, JSONDecodeError):
        TREE = init_tree()
    try:
        run_program(TREE)
    except InvalidArgumentException:
        input("Close the previous browser window and then press enter.")
        run_program(TREE)
    finally:
        TREE.write_to_file()
        # sort_to_folder_from_tree(TREE)


if __name__ == "__main__":
    main()
