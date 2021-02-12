import unittest
from pprint import pprint

from bfetch.modules.filetree import File, FileTree, Node, dic_to_tree

class TestTransform(unittest.TestCase):
    """
    Makes sure that dic_to_tree does not modify it's dictionary argument.
    """

    def test_leave_dict_unchanged(self):
        d1 = {
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
        d2 = {
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

        dic_to_tree(d1)

        # pprint(d1)
        # pprint(d2)
        # Should not have any side effects.
        self.assertEqual(d1, d2)

if __name__ == "__main__":
    unittest.main()
