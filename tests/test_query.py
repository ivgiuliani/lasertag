import unittest
from sqlobject import sqlhub

import lasertag


def test_setup():
    try:
        conn = sqlhub.getConnection()
        conn.close()
    except AttributeError:
        # Unhelpfully, we receive an `AttributeError` when the connection
        # wasn't estabilished before rather than a return value.
        pass

    lasertag.prepare(lasertag.IN_MEMORY_SQLITE)


def test_populate():
    lasertag.add_value(["source:http", "userid:123", "type:image"], "image1.jpg")
    lasertag.add_value(["source:http", "userid:345", "type:description"], "desc1")
    lasertag.add_value(["source:http", "userid:345", "type:image"], "image2.jpg")
    lasertag.add_value(["source:http", "userid:456", "type:image"], "image3.jpg")
    lasertag.add_value(["source:sftp", "host:bank.com", "category:control"], "bank-thing1")


class AddValueTest(unittest.TestCase):
    def setUp(self):
        test_setup()

    def test_individual_tags_are_added(self):
        lasertag.add_value(["t1", "t2"], "hello world")
        self.assertTrue("hello world" in lasertag.query(["t1"]))
        self.assertTrue("hello world" in lasertag.query(["t2"]))
        self.assertTrue("hello world" in lasertag.query(["t1", "t2"]))

    def test_no_duplicate_pairs(self):
        lasertag.add_value(["t1"], "v")
        lasertag.add_value(["t2"], "v")
        with self.assertRaises(AttributeError):
            lasertag.add_value(["t1"], "v")


class QueryTest(unittest.TestCase):
    def setUp(self):
        test_setup()
        test_populate()

    def test_query_single_tag_with_single_matching_value(self):
        self.assertListEqual(["bank-thing1"], lasertag.query(["host:bank.com"]))

    def test_query_single_tag_with_multiple_matching_values(self):
        self.assertListEqual(["image1.jpg", "image2.jpg", "image3.jpg"],
                             lasertag.query(["type:image"]))

    def test_query_multiple_tags_with_single_matching_value(self):
        self.assertListEqual(["bank-thing1"], lasertag.query(["host:bank.com", "source:sftp"]))

    def test_query_multiple_tags_with_multiple_matching_values(self):
        self.assertListEqual(["desc1", "image2.jpg"],
                             lasertag.query(["source:http", "userid:345"]))

    def test_empty_query(self):
        with self.assertRaises(AttributeError):
            lasertag.query([])

    def test_query_invalid_tag(self):
        self.assertListEqual([], lasertag.query(["invalid"]))

    def test_query_existing_tag_with_no_results(self):
        self.assertListEqual([], lasertag.query(["source:http", "host:bank.com"]))


class TagsTest(unittest.TestCase):
    def setUp(self):
        test_setup()
        test_populate()

    def test_returns_all_tags_for_existing_value(self):
        self.assertListEqual(["source:http", "userid:456", "type:image"],
                             lasertag.tags("image3.jpg"))

    def test_returns_empty_list_for_invalid_value(self):
        self.assertListEqual([], lasertag.tags("doesntexist"))


if __name__ == "__main__":
    unittest.main()
