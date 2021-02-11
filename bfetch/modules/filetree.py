from typing import List, Optional, Any, Dict, Tuple
import uuid
import json
from pprint import pprint

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
        return self.data == other.data

    def __str__(self):
        return f"{self.data}" + f"\n{self.kind}"


class Node:
    def __init__(self, file_object: File):
        self.file = file_object
        self.name = file_object.name
        self.id = self.name + (
            str(tuple(d for d in self.file.data.values()).__hash__())
        )
        # Whether this node has been downloaded

        self.parent: Optional[Node] = None
        self.children: List[Node] = []

    def __str__(self):
        return f'Node "{self.name}" {len(self.children)} children'

    def __eq__(self, other):
        return self.file == other.file

    # @property
    # def id(self):
    #     if hasattr(self, "identifier"):
    #         return self.identifier
    #     else:
    #         return self.name + str(uuid.uuid1())

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

    @property
    def root(self):
        return self.nodes[0]

    def add(self, node: Node, parent_node: Optional[Node]) -> None:
        """
        Adds the node to self.nodes. Set's the new node's parent.
        """

        if parent_node:
            a = f"\nchild_kind:{node.file.kind}, parent_kind:{parent_node.file.kind}"
            b = f"\nchild_type {node.node_type}, parent_type: {parent_node.node_type}"
            c = f"\nchild_name {node.name}, parent_name: {parent_node.name}"
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

    def attach_pointer(self, node: Optional[Node]) -> None:
        if node:
            self.pointer = node
            return None
        else:
            return None

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

    def __str__(self) -> str:
        def depth_traversal(source_node) -> List[str]:
            strings: List[str] = []
            stack: List[Tuple[Node, int]] = []
            visited: Dict[str, bool] = {n.id: False for n in self.nodes}

            stack.append((source_node, 0))

            while stack:
                n, level = stack.pop()

                if not visited[n.id]:
                    string = ("\t" * level) + f"{n.name}"
                    strings.append(string)
                    visited[n.id] = True

                # children = n.parent.children if n.node_type != "root" else []

                if (
                    all([not visited[c.id] for c in n.children])
                    and n.children != []
                ):
                    level += 1

                for child in reversed(n.children):
                    if not visited[child.id]:
                        stack.append((child, level))

            return strings

        strings = depth_traversal(self.root)

        return "\n".join(strings)

    def print_subtree(self, node):
        def depth_traversal(source_node) -> List[str]:
            strings: List[str] = []
            stack: List[Tuple[Node, int]] = []
            visited: Dict[str, bool] = {n.id: False for n in self.nodes}

            stack.append((source_node, 0))

            while stack:
                n, level = stack.pop()

                if not visited[n.id]:
                    string = ("\t" * level) + f"{n.name}"
                    strings.append(string)
                    visited[n.id] = True

                # children = n.parent.children if n.node_type != "root" else []

                if (
                    all([not visited[c.id] for c in n.children])
                    and n.children != []
                ):
                    level += 1

                for child in reversed(n.children):
                    if not visited[child.id]:
                        stack.append((child, level))

            return strings

        strings = depth_traversal(node)

        print("\n".join(strings))

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

    def dictionary(self) -> Dict[str, dict]:
        """
        Converts tree to dictionary.
        For non-file nodes, puts {node.file.name}.self
        entry one level below.
        """

        def recurse(self, dic: dict, sub_dic: dict, top_node: Node) -> dict:
            """
            dic is the dictionary that accumulates through
            the recursion.
            sub_dic is the dictionary inside
            """

            # BASE CASE
            if top_node.node_type == "leaf":
                return top_node.file.data

            if sub_dic == {} and dic == {}:  # For first call.
                dic[top_node.name] = {}
                new_sub_dic = dic[top_node.name]

            if top_node.node_type == "root":
                sub_dic[top_node.name] = {}
                new_sub_dic = sub_dic[top_node.name]
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
def dic_to_tree(dic: Dict[str, dict]) -> FileTree:
    """
    Takes a dictionary and converts it to a tree.
    """

    def recurse(sub_dic: Dict[str, dict], parent_node: Node) -> None:
        for d in sub_dic:

            if f"{d}.self" in sub_dic[d]:  # If this is a section.
                data = sub_dic[d][f"{d}.self"]
                name = data["name"]
                url = data["url"]
                kind = data["kind"]
                file_name = data["file_name"]
                assert type(file_name) is str or file_name is None
                completed = data["completed"]
                assert type(completed) is bool
                node = Node(File(name, url, kind, completed, file_name))
                tree.insert(node, parent_node)

                # Iterate through the rest of the tree,
                # Basically this is removing the section
                # header.
                rest_of_sub_dic = {
                    i: sub_dic[d][i] for i in sub_dic[d] if i != f"{d}.self"
                }
                # sub_dic[d].pop(f"{d}.self", None)
                if rest_of_sub_dic:
                    recurse(rest_of_sub_dic, node)
                else:
                    continue
            else:
                data = sub_dic[d]
                name = data["name"]
                url = data["url"]
                kind = data["kind"]
                file_name = data["file_name"]
                completed = data["completed"]
                node = Node(File(name, url, kind, completed, file_name))
                tree.insert(node, parent_node)

    tree = FileTree([Node(File("root", "", "root"))])
    recurse(dic, tree.root)
    # for module in dic:
    #     module_node = Node(File(module, "", "module"))
    #     tree.insert(module_node, tree.root)
    #     recurse(dic[module], module_node)
    return tree


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
    treep = dic_to_tree(test_dic)
    with open(
        "/home/carneca/Documents/Python/automation/bfetch/bfetch/tests/files/complicated_dictionary.json",
        "r",
    ) as f:
        dic = json.load(f)

        t = dic_to_tree(dic)
        print(t.__str__())
