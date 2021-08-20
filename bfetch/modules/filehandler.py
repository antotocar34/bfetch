from typing import Optional, IO
from bfetch.modules.filetree import File, FileTree, Node

from collections import deque

import os
from pathlib import Path

from timeout_decorator import timeout
from timeout_decorator.timeout_decorator import TimeoutError
from selenium.webdriver.chrome.webdriver import WebDriver

from bfetch.modules.head_request import head_request
import bfetch.modules.config as g
from bfetch.modules.utils import normalize_name, get_request



class FilePath:
    """
    Contains the Aspects of the file's
    destination path.
    """
    dl_dir = Path(g.DOWNLOAD_PATH)

    def __init__(self, destination_path: str):
        self.destination_path = Path(destination_path)

        self.final_name = self.destination_path.name

        self.download_name: Optional[str] = None
        
    def downloading(self) -> bool:
        if "crdownload" in self.destination_path.suffix:
            return True
        else:
            return False

def constructFilePath(tree: FileTree, node: Node) -> FilePath:
    return FilePath(file_node_to_path(tree, node))

class Downloader:
    def __init__(self):
        self.downloaded = []

    
    def download_file(self, browser: WebDriver, node: Node) -> bool:

        get_request(browser, node.file.url)

        dl_dir = Path(g.DOWNLOAD_PATH)

        @timeout(30)
        def wait_for_file_to_appear():
            # Wait for download to finish.
            file_path: Optional[Path] = None
            while not file_path or "crdownload" in file_path.suffix:
                try:
                    files = [(f.stat().st_mtime, f) for f in dl_dir.iterdir()]
                except FileNotFoundError:  # In case file completes
                    # while `files` is being evaluated.
                    continue

                # file_path: Path
                _, file_path = max(files)
            return file_path


        try:
            file_path = wait_for_file_to_appear()

            self.downloaded.append(file_path)

            node.file.file_name = file_path.name

            node.file.completed = True
            print(f"DOWNLOADED : {node.file.file_name}")
            return True
        except TimeoutError:
            return False
            

def download_file(browser: WebDriver, node: Node) -> None:
    """
    Downloads file_node.
    """

    try:
        file_name, file_type = head_request(browser, node.file.url)
    except:
        pass

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


def download_file_nodes(browser: WebDriver, tree: FileTree) -> None:
    """
    Goes through the tree and downloads nodes that have not been downloaded.
    """
    file_nodes = [
        n
        for n in tree.nodes
        if n.file.kind == "file" and n.file.completed == False
    ]

    for n in file_nodes:
        download_file(browser, n)
    return None

def file_node_to_path(tree: FileTree, node: Node) -> str:
    """
    Given a  tree of the form

           root
           /  \
          m1   m2
         /
        s1
       /
      f1
    
    and the node 1, returns

    m1.name/s1.name/f1.file.name

    """
    assert node.file.kind == "file"
    assert node.file.file_name is not None

    nodes = []

    def find_module_node(node: Optional[Node]) -> Optional[Node]:
        if node.file.kind == "module":
            module_node = node
            nodes.append(module_node)
            return node
        else:
            nodes.append(node)
            find_module_node(node.parent)
            return None

    find_module_node(node)
    nodes.reverse()

    def path_name(node) -> str:
        if node.file.kind != "file":
            return node.file.name
        else:
            return node.file.file_name


    names = [path_name(n) for n in nodes]
    path = f"{g.DOWNLOAD_PATH}/" + "/".join(names)

    return path


def move_file_to_path(node_path: str, new_name: str) -> bool:
    """
    Takes a path and moves the name of the file in that path
    and moves dl_dir/file_name to path.

    Returns True if file is moved successfully or if
    the file already exists in the desired location.
    If there was some sort of problem returns False.
    """
    # Checks that the path exists.

    dl_dir = Path(g.DOWNLOAD_PATH)
    p = Path(node_path)

    file_dirs = p.parent
    file_name = p.name
    new_file_name = Path(new_name)

    new_path: Path = p.parent / new_file_name

    # Does the exist in the dl directory.
    if (dl_dir / file_name).exists():
        if p.parent.exists() == False:
            p.parent.mkdir(parents=True, exist_ok=True)
        (dl_dir / file_name).replace(new_path)
        return True
    # Has the file already been moved for some reason.
    elif new_path.exists():
        return True
    else:
        return False


def handle_file_node(tree: FileTree, node: Node) -> bool:
    path = file_node_to_path(tree, node)
    # Moves specific file node ot path

    assert node.file.file_name is not None
    new_name = normalize_name(node.file.file_name)
    exit = move_file_to_path(path, new_name)
    return exit

def sort_to_folder_from_tree(tree: FileTree) -> None:
    """
    Finds all file nodes and sorts them to the appropriate folder.
    """

    tree_files = [n for n in tree.nodes 
                  if n.file.kind == "file" and n.file.completed == True]

    for file_node in tree_files:
        satisfied_bool = handle_file_node(tree, file_node)
        # Whether file was moved properly.
        file_node.satisfied = satisfied_bool
