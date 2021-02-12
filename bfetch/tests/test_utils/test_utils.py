import unittest
import pytest

from bfetch.modules.utils import make_wfu



class TestUtils(unittest.TestCase):


    def wfu_test1(self):

        input_url = "/bbcwebdav/xid-12039823-pid"

        expected_url = f"https://www.tcd.blackboard.come/{input_url}"

        output_url = make_wfu(input_url)

        self.assertEqual(output_url, expected_url)

    def wfu_test2(self):

        input_url = "https://www.google.com/whatever-shite"

        expected_url = input_url

        output_url = make_wfu(input_url)

        self.assertEqual(output_url, expected_url)

    def wfu_test3(self):

        input_url = "https://www.tcd.blackboard.com/lkdjflsdkfjlsdfj-lkjdflksjfd"

        expected_url = input_url

        output_url = make_wfu(input_url)

        self.assertEqual(output_url, expected_url)
