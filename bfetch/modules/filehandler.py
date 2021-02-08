from typing import Optional
from modules.general_tree import File, FileTree, Node

import os

try:
    import modules.config as g
except:
    import config as g

from pathlib import Path


def newest(path: str=g.DOWNLOAD_PATH):
    """
    Retrieves the newest file in
    the path. Directories are excluded.
    """
    files = os.listdir(path)
    paths = [f"{path}/{f}" for f in next(os.walk(path))[2]]
    if paths:
        # Wait until file is downloaded.
        while max(paths, key=os.path.getctime) is not None:
            return max(paths, key=os.path.getctime)
    else:
        print("Nothing here")


def file_node_to_path(tree: FileTree, node: Node) -> str:
    """
    returns the path from tree node.
    """
    assert node.file.kind == "file"
    assert node.file.file_name is not None

    nodes = []

    def find_module_node(node: Node) -> Optional[Node]:
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


# TODO investigate how the path should be return with normalized name
def move_file_to_path(path: str) -> None:
    """
    Takes a path and moves the name of the file in that path
    and moves dl_dir/file_name to path.
    """
    # Checks that the path exists.

    dl_dir = Path(g.DOWNLOAD_PATH)
    p = Path(path)

    try:
        assert (dl_dir / p.name).exists()

        if p.parent.exists() == False:
            p.parent.mkdir(parents=True, exist_ok=True)
            (dl_dir / p.name).replace(p)
        else:
            (dl_dir / p.name).replace(p)
    except AssertionError:
        if p.exists():
            return
        else:
            print("THERE WAS A POTENTIAL PROBLEM")
            return 

def handle_file_node(tree: FileTree, node: Node) -> None:
    path = file_node_to_path(tree, node)
    move_file_to_path(path)
    # Moves specific file node ot path


def sort_to_folder_from_tree(tree: FileTree) -> None:
    """
    Finds all file nodes and sorts them to the appropriate folder.
    """

    tree_files = [n for n in tree.nodes if n.file.kind == "file"]
    for file_node in tree_files:
        handle_file_node(tree, file_node)

