import json
import unittest
from pprint import pprint

import bfetch.modules.config as g
from bfetch.modules.filetree import Node, File, FileTree
from bfetch.modules.filetree import load_tree_from_file, dic_to_tree


def get_complicated_dictionary() -> dict:
    file_path = f"{g.CODE_DIR}/tests/files/complicated_dictionary.json"
    with open(file_path, 'r') as f:
        dic = json.load(f)
        return dic
        


class TestTree(unittest.TestCase):
    def test_index_method(self):
        """
        Tests that tree[name_of_node] works.
        """
        tree= self.test_tree
        self.assertEqual(self.file1a, tree[self.file1a.name])


    root = Node(File("root", "", "root"))
    mod1 = Node(File("module1", "", "module"))
    sec1 = Node(File("section1", "", "section"))
    file1a = Node(File("file1a", "", "file"))
    file1b = Node(File("file1b", "", "file"))

    test_tree = FileTree()
    test_tree.insert(root)
    test_tree.insert(mod1, root)
    test_tree.insert(sec1, mod1)
    test_tree.insert(file1a, sec1)
    test_tree.insert(file1b, sec1)

    t_root = Node(File("root", "", "root"))
    t_mod1 = Node(File("module1", "", "module"))
    t_sec1 = Node(File("section1", "", "section"))
    t_file1a = Node(File("file1a", "", "file"))
    t_file1b = Node(File("file1b", "", "file"))

    t_root.children.append(t_mod1)

    t_mod1.parent = t_root
    t_mod1.children.append(t_sec1)

    t_sec1.parent = t_mod1


    t_file1a.parent = t_sec1
    t_file1b.parent = t_sec1

    t_sec1.children.append(t_file1a)
    t_sec1.children.append(t_file1b)


    good_tree = FileTree([t_root, t_mod1, t_sec1, t_file1a, t_file1b])

    good_dict = {
            "module1" : {
                "module1.self" : {
                    "name" : "module1",
                    "url"  : "",
                    "kind" : "module",
                    "file_name" : None,
                    "completed" : False
                    },
                "section1": {
                    "section1.self" : {
                        "name" : "section1",
                        "url"  : "",
                        "kind" : "section",
                        "file_name" : None,
                        "completed" : False
                        },
                    "file1a" : {
                        "name" : "file1a",
                        "url"  : "",
                        "kind" : "file",
                        "file_name" : None,
                        "completed" : False
                        },
                    "file1b" : {
                        "name" : "file1b",
                        "url"  : "",
                        "kind" : "file",
                        "file_name" : None,
                        "completed" : False
                        }
                    }
                }
            }

    # def test_insert_large(self):
    #     """
    #     Tests that basic tree construction works.
    #     """
    #     # __str__ instance will contain all that is needed for
    #     # the tree to work.
    #     self.assertEqual(
    #             self.test_tree.__str__(), self.good_tree.__str__()
    #     )

    def test_tree_to_dic(self):
        tree = self.test_tree
        test_dic = tree.dictionary()
        good_dict = self.good_dict.copy()

        print("EXPECTED: ")
        pprint(good_dict)
        print("OUTPUT: ")
        pprint(test_dic)
        self.assertEqual(test_dic, good_dict)



    def test_dic_to_tree_simple(self):
        # pprint(self.test_dic)
        good_dict = {
                "module1" : {
                    "module1.self" : {
                        "name" : "module1",
                        "url"  : "",
                        "kind" : "module",
                        "file_name" : None,
                        "completed" : False
                        },
                    "section1": {
                        "section1.self" : {
                            "name" : "section1",
                            "url"  : "",
                            "kind" : "section",
                            "file_name" : None,
                            "completed" : False
                            },
                        "file1a" : {
                            "name" : "file1a",
                            "url"  : "",
                            "kind" : "file",
                            "file_name" : None,
                            "completed" : False
                            },
                        "file1b" : {
                            "name" : "file1b",
                            "url"  : "",
                            "kind" : "file",
                            "file_name" : None,
                            "completed" : False
                            }
                        }
                    }
                }

        test_tree = dic_to_tree(good_dict)
        self.assertEqual(test_tree.__str__(),
                         self.good_tree.__str__())


    def test_lossless_tree_dict_tree(self):
        """
        If A: tree -> B: dict -> C: tree
      
        Checks that A == C.
        """

        A = self.good_tree

        B = A.dictionary()

        C = dic_to_tree(B)

        cond1 = all([n1 == n2 for n1,n2 in zip(A.nodes,C.nodes)])
        self.assertTrue(cond1)



    def test_lossless_dict_tree_dict(self):
        """
        If A: dict -> B: tree -> C: dict
      
        Checks that A == C.
        """
        good_dict = {
                "module1" : {
                    "module1.self" : {
                        "name" : "module1",
                        "url"  : "",
                        "kind" : "module",
                        "file_name" : None,
                        "completed" : False
                        },
                    "section1": {
                        "section1.self" : {
                            "name" : "section1",
                            "url"  : "",
                            "kind" : "section",
                            "file_name" : None,
                            "completed" : False
                            },
                        "file1a" : {
                            "name" : "file1a",
                            "url"  : "",
                            "kind" : "file",
                            "file_name" : None,
                            "completed" : False
                            },
                        "file1b" : {
                            "name" : "file1b",
                            "url"  : "",
                            "kind" : "file",
                            "file_name" : None,
                            "completed" : False
                            }
                        }
                    }
                }
        p = good_dict.copy() 
        # pprint(p)

      
        tree_from_dict = dic_to_tree(good_dict)
        # print([n.file.data for n in tree_from_dict.nodes])
        transformed = tree_from_dict.dictionary()
        # pprint(transformed)
        self.assertEqual(transformed, good_dict)


    def test_dic_to_tree_complex(self):
        """
        Tests a real dictionary.
        """
        good_dict = get_complicated_dictionary()
        tree = dic_to_tree(good_dict)
        # print(tree)
        recycled_dict = tree.dictionary()
        # pprint(good_dict)
        # pprint(recycled_dict)
        self.assertEqual(good_dict, recycled_dict)

    def test_string_dunder_method(self):
        complicated_dictionary = get_complicated_dictionary()
        tree = dic_to_tree(complicated_dictionary)
        string = tree.__str__()
        self.assertIs(type(string), str)

    def test_load_tree_from_file(self):
        file_path = f"{g.CODE_DIR}/tests/files/complicated_dictionary.json"
        tree = load_tree_from_file(file_path)
        print(tree)
        self.assertIs(type(tree), FileTree)


if __name__ == "__main__":
    unittest.main()
