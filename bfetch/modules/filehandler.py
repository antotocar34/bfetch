from typing import Optional
from modules.filetree import File, FileTree, Node

import os
from pathlib import Path

import modules.config as g
from modules.utils import normalize_name



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


# TODO investigate how the path should be return with normalized name
def move_file_to_path(node_path: str, new_name: str) -> None:
    """
    Takes a path and moves the name of the file in that path
    and moves dl_dir/file_name to path.
    """
    # Checks that the path exists.

    dl_dir = Path(g.DOWNLOAD_PATH)
    p: Path = Path(node_path)

    file_dirs = p.parent
    file_name = p.name
    new_file_name = Path(new_name)

    new_path: Path = p.parent / new_file_name

    try:
        assert (dl_dir / file_name).exists()

        if p.parent.exists() == False:
            p.parent.mkdir(parents=True, exist_ok=True)
        (dl_dir / file_name).replace(new_path)
    except AssertionError:
        if new_path.exists():
            return
        else:
            print(f"{p.name}")
            print("THERE WAS A POTENTIAL PROBLEM")
            return 

def handle_file_node(tree: FileTree, node: Node) -> None:
    path = file_node_to_path(tree, node)
    # Moves specific file node ot path

    assert node.file.file_name is not None
    new_name = normalize_name(node.file.file_name)
    move_file_to_path(path, new_name)


def sort_to_folder_from_tree(tree: FileTree) -> None:
    """
    Finds all file nodes and sorts them to the appropriate folder.
    """

    tree_files = [n for n in tree.nodes if n.file.kind == "file"]
    for file_node in tree_files:
        handle_file_node(tree, file_node)

