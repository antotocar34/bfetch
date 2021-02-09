from typing import List, Optional, Any
import uuid
import json

import modules.config as g
# import config as g


class File:
    """
    Contains data for nodes. That's it.
    """

    def __init__(
        self,
        name: str,
        url: str,
        kind: str,
        completed: bool = False,
        file_name: Optional[str] = None,
    ):
        # Name of tag
        self.name = name
        self.file_name = file_name
        self.url = url
        assert kind in ["root", "module", "section", "file"]
        self.kind = kind
        self.completed = completed

    @property
    def data(self):
        data = {
            "url": self.url,
            "name": self.name,
            "kind": self.kind,
            "file_name": self.file_name,
            "completed": self.completed,
        }
        return data

    def __eq__(self, other):
        return self.data == other.data and self.kind == other.kind

    def __str__(self):
        return f"{self.data}" + f"\n{self.kind}"


class Node:
    def __init__(self, file_object: File):
        self.file = file_object
        self.name = file_object.name
        # Whether this node has been downloaded

        self.parent: Optional[Node] = None
        self.children: List[Node]  = []

    def __str__(self):
        return f'Node "{self.name}" {len(self.children)} children'

    def __eq__(self, other):
        return self.file == other.file

    @property
    def identifier(self) -> str:
        return self.name

    @property
    def node_type(self) -> str:
        if self.children == [] and self.parent is not None:
            return "leaf"
        elif self.parent is None:
            return "root"
        else:
            return "subtree"


def check_validity_of_order(child_node: Node, parent_node: Node) -> bool:
    """
    node -> node -> Bool
    Assures that inserts make sense.
    """
    if parent_node is None:
        return True

    # kinds -> [file, section, module, root]
    if parent_node.file.kind == "root":
        if child_node.file.kind == "module":
            return True
        else:
            return False
    if parent_node.file.kind == "module":
        if child_node.file.kind == "section":
            return True
        else:
            return False
    if parent_node.file.kind == "section":
        if any([child_node.file.kind == k for k in ["section", "file"]]):
            return True
        else:
            return False
    if parent_node.file.kind == "file":
        return False
    else:
        return False


class FileTree:
    def __init__(self, nodes: List[Node] = []):
        self.nodes = nodes
        self.pointer = None

    def add(self, node: Node, parent_node: Optional[Node]) -> None:

        if parent_node:
            a = f"\nchild:{node.file.kind}, parent:{parent_node.file.kind}"
            b = f"\nchild_type {node.node_type}, parent: {parent_node.node_type}"
            c = f"\nchild_type {node.name}, parent: {parent_node.name}"
            assert check_validity_of_order(node, parent_node), a + b + c

            
            if self.nodes != []:
                node.parent = parent_node
                parent_node.children.append(node)

        self.nodes.append(node)

    def insert(self, node: Node, parent_node: Optional[Node] = None) -> None:
        """
        Adds the node to the tree, from the parent node.
        Move the pointer to that tree.
        """
        self.add(node, parent_node)

        self.attach_pointer(node)

    def attach_pointer(self, node : Optional[Node]) -> None:
        if node:
            self.pointer = node
            return None
        else:
            return None

    def get_subtree(self, node: Node):
        return FileTree(self.get_children(node))

    def get_children(self, node: Node) -> List[Node]:
        assert node in self.nodes, "Node not in tree."
        S = [node]
        for child in node.children:
            S = S + self.get_children(child)
        return S

    def get_index(self, identifier: str) -> int:
        """ Searches by identifier, which is usually just the name"""
        for index, node in enumerate(self.nodes):
            if node.name == identifier:
                return index
        else:
            raise KeyError

    def __getitem__(self, name: str):
        return self.nodes[self.get_index(name)]

    def __len__(self):
        """Number of nodes in the tree"""
        return len(self.nodes)

    def __eq__(self, other) -> bool:
        return self.nodes == other.nodes

    @property
    def root(self):
        return self.nodes[0]

    def __str__(self):
        string = []

        def tree_to_string(tree, name="root", level=0) -> None:
            queue = self[name].children
            if level == 0:
                str_name = self[name].name
                nonlocal string
                string.append(str_name)
                # print(f"{self[name].name}")
            else:
                str1 = "\t" * level
                str2 = f"{self[name].name}"
                str_name = f"{str1} {str2}"
                string.append(str_name)
                # print("\t" * level, f"{self[name].name}")
            level += 1
            for element in queue:
                tree_to_string(tree, element.name, level)  # recursive call

        tree_to_string(self)
        return "\n".join(string)


    def get_module(self, node) -> Node:
        """
        Get's the module directory of current node.
        Error if root node is passed in.
        """
        assert node != self.root, "Root node"

        if node.file.kind != "module":
            return self.get_module(node.parent)
        else:
            return node

    def dictionary(self) -> dict:
        """
        tree -> dict
        """

        def recurse(self, dic: dict, sub_dic: dict, top_node: Node):

            # BASE CASE
            if top_node.node_type == "leaf":
                return top_node.file.data

            if sub_dic == {} and dic == {}:  # For first call.
                dic[top_node.name] = {}
                new_sub_dic = dic[top_node.name]

            else:
                # Initialize new node dictionary, and reassign sub_dic
                sub_dic[top_node.name] = {}
                sub_dic[top_node.name][
                    f"{top_node.name}.self"
                ] = top_node.file.data
                new_sub_dic = sub_dic[top_node.name]

            # GENERAL CASE
            if top_node.node_type != "leaf":
                for child in top_node.children:
                    new_sub_dic[child.name] = recurse(
                        self, dic, new_sub_dic, child
                    )

            return new_sub_dic

        d = recurse(self, {}, {}, self.root)

        return d

    def write_to_file(self):
        with open(f"{g.DATA_DIR}/structure.json", "w") as outfile:
            json.dump(self.dictionary(), outfile, indent=4)


# TODO finish this
def dic_to_tree(dic: dict):
    def recurse(sub_dic: dict, parent_node: Node):
        for d in sub_dic:
            if f"{d}.self" in sub_dic:  # If this is a section.
                data = sub_dic[d][f"{d}.self"]
                node = Node(File(d, data["url"], data["kind"]))
                tree.insert(node, parent_node)
                recurse(sub_dic[d], node)
            else:
                data = sub_dic[d]
                node = Node(File(d, data["url"], data["kind"]))
                tree.insert(node, parent_node)

    # Losing information about the url. Does it matter?
    tree = FileTree([Node(File("root", "", "root"))])
    for module in dic:
        module_node = Node(File(module, "", "module"))
        tree.insert(module_node, tree.root)
        recurse(dic[module], module_node)


if __name__ == "__main__":

    test_dic = {
        "economics": {
            "economics.self": {
                "url": "tcd.ie",
                "name": "economics",
                "kind": "module",
                "file_name": None,
                "completed": False,
            },
            "lectures": {
                "lectures.self": {
                    "url": "tcd.ie",
                    "name": "lectures",
                    "kind": "section",
                    "file_name": None,
                    "completed": False,
                },
                "hi.pdf": {
                    "url": "tcd.ie",
                    "name": "hi.pdf",
                    "kind": "file",
                    "file_name": None,
                    "completed": False,
                },
                "descartes.pdf": {
                    "url": "tcd.ie",
                    "name": "descartes.pdf",
                    "kind": "file",
                    "file_name": None,
                    "completed": False,
                },
                "solutions": {
                    "solutions.self": {
                        "url": "tcd.ie",
                        "name": "solutions",
                        "kind": "section",
                        "file_name": None,
                        "completed": False,
                    },
                    "kripke.pdf": {
                        "url": "tcd.ie",
                        "name": "kripke.pdf",
                        "kind": "file",
                        "file_name": None,
                        "completed": False,
                    },
                },
            },
        }
    }
