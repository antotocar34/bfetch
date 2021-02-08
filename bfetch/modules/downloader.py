from modules.general_tree import FileTree, Node, File
from main import download_file
from selenium.webdriver.chrome.webdriver import WebDriver


def walk_through_tree_and_download(browser: WebDriver, tree: FileTree) -> None:
    files = [
        n for n in tree.nodes
        if n.file.kind == "file" and n.file.completed == False
    ]

    for n in files:
        download_file(browser, n)
