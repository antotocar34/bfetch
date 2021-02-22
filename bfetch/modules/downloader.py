"""
This module does the following.

Defines a downloader class. Which keeps track of the downloads,
allowing it to decide what was not downloaded properly, and label
those things appropriately.


The FilePath class holds the information about what the file's
name is keeping all of the necessary information..
"""

from typing import Optional, List
from pathlib import Path


from timeout_decorator import timeout
from selenium.webdriver.chrome.webdriver import WebDriver

from bfetch.modules.utils import get_request, normalize_name
from bfetch.modules.filetree import FileTree, Node, File
import bfetch.modules.config as g


# Downloader should download the file and the move it in one go.


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


class FilePath:
    """
    Contains the Aspects of the file's
    destination path.

    Contains a method to move the file to the correct path.
    """

    dl_dir = Path(g.DOWNLOAD_PATH)

    def __init__(self, node: Node, tree: FileTree):

        destination_path_str = file_node_to_path(tree, node)

        # Path to move file_to, has the name been normalized?
        self.destination = Path(destination_path_str)

        self.final_name = self.destination.name

        # Only retrieved after downloading, (or from header request).
        self.download_name: Optional[str] = node.file.file_name


    @property
    def download_location(self):
        assert self.download_name != None

        return self.dl_dir / Path(self.download_name)


class Downloader:

    dl_dir = Path(g.DOWNLOAD_PATH)

    def __init__(self):
        self.downloaded: List[str] = []

    def get(self, browser, node) -> None:
        get_request(browser, node)

    @timeout(g.DOWNLOAD_TIMEOUT)
    def wait_for_file_to_appear(self) -> Path:
        # Wait for download to finish.
        file_path: Optional[Path] = None
        # in dl_dir?
        while (
            # First call.
            not file_path
            # File is downloading.
            or "crdownload" in file_path.suffix
            # In case file does not download at all.
            # Don't match most recent downloaded.
            or file_path == self.downloaded[-1]
        ):
            try:
                # Check for the most recently downloaded file
                files = [(f.stat().st_mtime, f) for f in self.dl_dir.iterdir()]
            except FileNotFoundError:  # In case file completes
                # while `files` is being evaluated.
                continue

            # file_path: Path
            _, file_path = max(files)

        return file_path

    def download_file(self, browser: WebDriver, node: Node) -> bool:
        """
        Returns True if file was successfully downloaded.
        Returns False if file was not successfully downloaded.
        """

        # Better download functions need to be tested.
        self.get(browser, node.file.url)

        try:
            file_path = self.wait_for_file_to_appear()

            self.downloaded.append(str(file_path))

            node.file.file_name = file_path.name

            node.file.completed = True
            print(f"DOWNLOADED : {node.file.file_name}")
            return True
        except TimeoutError:
            print("failed to downlaod the file")
            return False


    def sort_file(self, node: Node, tree: FileTree) -> bool:
        """
        Returns True if file is sorted or if the file has already been sorted.
        Otherwise returns false.
        """

        fp = FilePath(node, tree)

        # Does the file exist in the dl directory.
        if fp.download_location.exists():

            # Create the dl directory if it has not already been created.
            if fp.destination.parent.exists() == False:
                fp.destination.parent.mkdir(parents=True, exist_ok=True)

            fp.download_location.replace(fp.destination)
            return True
        # Has the file already been moved for some reason.
        elif fp.destination.exists():
            return True
        else:
            return False


    def download_and_sort(self, 
                          node: Node,
                          browser: WebDriver, 
                          tree: FileTree) -> bool:

        exit_status = self.download_file(browser, node)
        if exit_status:
            exit_bool = self.sort_file(node, tree)
            return exit_bool
        else:
            return False


def download_nodes(browser: WebDriver, tree: FileTree):
    to_download = [n for n in tree.nodes
                   if n.file.completed == False]

    downloader = Downloader()
    for node in to_download:
        exit_bool = downloader.download_and_sort(node, browser, tree)
        node.file.completed = exit_bool
