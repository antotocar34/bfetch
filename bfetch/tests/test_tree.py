import unittest

from modules.general_tree import Node, File, FileTree


class TestTree(unittest.TestCase):
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

    t_root.children.append(mod1)

    t_mod1.parent = t_root
    t_mod1.children.append(t_sec1)

    t_sec1.parent = t_mod1


    t_file1a.parent = t_sec1
    t_file1b.parent = t_sec1

    t_sec1.children.append(t_file1a)
    t_sec1.children.append(t_file1b)


    good_tree = FileTree([t_root, t_mod1, t_sec1, t_file1a, t_file1b])

    def test_insert_large(self):
        """
        Tests that basic tree construction works.
        """


        self.assertTrue(
                self.test_tree.__str__() == self.good_tree.__str__()
        )

        test_dic = {
                "mod1" : {
                    "sec1": {
                        "sec1.self" : {
                            "name" : "sec1",
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

        def test_dic_to_tree(self):
            pass


        def test_tree_to_dic(self):
            tree = self.test_tree
            dic = self.test_dic
            self.assertTrue(tree.dictionary() == dic)




if __name__ == "__main__":
    unittest.main()
