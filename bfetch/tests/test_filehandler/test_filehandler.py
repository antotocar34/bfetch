import unittest

from modules.filehandler import file_node_to_path
from modules.filetree import Node, File, FileTree
import modules.config as g


class TestFileHandler(unittest.TestCase):

    def test_file_node_to_path(self):


        root = Node(File("root", "", "root"))
        mod1 = Node(File("module1", "", "module"))
        sec1 = Node(File("section1", "", "section"))
        file1a = Node(File("file1a", "", "file"))
        file1b = Node(File("file1b", "", "file"))

        root.children.append(mod1)

        mod1.parent = root
        mod1.children.append(sec1)

        sec1.parent = mod1


        file1a.parent = sec1
        file1a.file.file_name = "file1a.pdf"
        file1b.parent = sec1

        sec1.children.append(file1a)
        sec1.children.append(file1b)

        tree = FileTree([root, mod1, sec1, file1a, file1b])

        output = file_node_to_path(tree, file1a)

        desired_output = f"{mod1.name}/{sec1.name}/{file1a.file.file_name}"
        desired_output = f"{g.DOWNLOAD_PATH}/{desired_output}"

        self.assertEqual(output, desired_output)

