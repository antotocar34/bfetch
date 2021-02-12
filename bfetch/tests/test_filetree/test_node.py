import unittest

from bfetch.modules.filetree import File, Node, FileTree


class TestNode(unittest.TestCase):


    def test_node_satisfied_property(self):

        node1 = Node(File("parent", "", "section"))

        node11 = Node(File("child1", "", "file"))
        node12 = Node(File("child2", "", "file"))

        node1.children = [node11, node12]

        for n in [node11, node12]:
            n.parent = node1


        node11.file.completed = True
        node12.file.completed = False


        cond = all([
            node1.satisfied == False,
            node11.satisfied == True,
            node12.satisfied == False
            ])

        self.assertTrue(cond)

        node12.file.completed = True

        self.assertTrue(node1.satisfied)

        return True
