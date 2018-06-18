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
    lasertag.add_value(["source:http", "userid:123", "type:image"],
                       "image1.jpg")
    lasertag.add_value(["source:http", "userid:345", "type:description"],
                       "desc1")
    lasertag.add_value(["source:http", "userid:345", "type:image"],
                       "image2.jpg")
    lasertag.add_value(["source:http", "userid:456", "type:image"],
                       "image3.jpg")
    lasertag.add_value(["source:sftp", "host:bank.com", "category:control"],
                       "bank-thing1")


class AddValueTest(unittest.TestCase):
    class TestTagTransformer(lasertag.BaseTransformer):
        def transform(self, tags, value, *args, **kwargs):
            return ["new", "tags"], value

    class TestValueTransfomer(lasertag.BaseTransformer):
        def transform(self, tags, value, *args, **kwargs):
            return tags, "new value"

    class TestTransfomer(lasertag.BaseTransformer):
        def transform(self, tags, value, *args, **kwargs):
            return ["new", "tags"], "new value"

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

    def test_empty_tags(self):
        with self.assertRaises(AttributeError):
            lasertag.add_value([], "v")

    def test_add_duplicate_rollsback_changes(self):
        lasertag.add_value(["a", "b", "c"], "v")
        with self.assertRaises(AttributeError):
            lasertag.add_value(["c", "d", "e", "f"], "v")
        self.assertEqual([], lasertag.query("d"))
        self.assertEqual([], lasertag.query("e"))
        self.assertEqual([], lasertag.query("f"))

    def test_add_with_tag_transformer(self):
        lasertag.add_value(["t1", "t2"], "value",
                           transformers=[self.TestTagTransformer()])

        self.assertEqual([], lasertag.query("t1"))
        self.assertEqual([], lasertag.query("t2"))
        self.assertEqual(["value"], lasertag.query(["new", "tags"]))

    def test_add_with_value_transformer(self):
        lasertag.add_value(["t1", "t2"], "value",
                           transformers=[self.TestValueTransfomer()])

        self.assertEqual([], lasertag.query("new"))
        self.assertEqual([], lasertag.query("tags"))
        self.assertEqual(["new value"], lasertag.query(["t1", "t2"]))

    def test_add_with_both_tag_and_value_transformer(self):
        lasertag.add_value(["t1", "t2"], "value",
                           transformers=[self.TestTransfomer()])

        self.assertEqual([], lasertag.query("t1"))
        self.assertEqual([], lasertag.query("t2"))
        self.assertEqual([], lasertag.tags("value"))
        self.assertEqual(["new value"], lasertag.query(["new", "tags"]))

    def test_add_empty_transformer_list(self):
        lasertag.add_value(["t1", "t2"], "hello world", transformers=[])
        self.assertTrue("hello world" in lasertag.query(["t1"]))
        self.assertTrue("hello world" in lasertag.query(["t2"]))
        self.assertTrue("hello world" in lasertag.query(["t1", "t2"]))

    def test_add_with_multiple_transfomers(self):
        lasertag.add_value(["t1", "t2"], "value",
                           transformers=[
                               self.TestTagTransformer(),
                               self.TestValueTransfomer()
                           ])

        self.assertEqual([], lasertag.query("t1"))
        self.assertEqual([], lasertag.query("t2"))
        self.assertEqual([], lasertag.tags("value"))
        self.assertEqual(["new value"], lasertag.query(["new", "tags"]))


class QueryTest(unittest.TestCase):
    def setUp(self):
        test_setup()
        test_populate()

    def test_query_single_tag_with_single_matching_value(self):
        self.assertListEqual(["bank-thing1"],
                             lasertag.query(["host:bank.com"]))

    def test_query_single_tag_with_multiple_matching_values(self):
        self.assertListEqual(["image1.jpg", "image2.jpg", "image3.jpg"],
                             lasertag.query(["type:image"]))

    def test_query_multiple_tags_with_single_matching_value(self):
        self.assertListEqual(["bank-thing1"],
                             lasertag.query(["host:bank.com", "source:sftp"]))

    def test_query_multiple_tags_with_multiple_matching_values(self):
        self.assertListEqual(["desc1", "image2.jpg"],
                             lasertag.query(["source:http", "userid:345"]))

    def test_empty_query(self):
        with self.assertRaises(AttributeError):
            lasertag.query([])

    def test_query_invalid_tag(self):
        self.assertListEqual([], lasertag.query(["invalid"]))

    def test_query_existing_tag_with_no_results(self):
        self.assertListEqual([],
                             lasertag.query(["source:http", "host:bank.com"]))

    def test_query_single_tag_given_as_string(self):
        self.assertListEqual(["desc1", "image2.jpg"],
                             lasertag.query("userid:345"))


class TagsTest(unittest.TestCase):
    def setUp(self):
        test_setup()
        test_populate()

    def test_returns_all_tags_for_existing_value(self):
        self.assertListEqual(["source:http", "userid:456", "type:image"],
                             lasertag.tags("image3.jpg"))

    def test_returns_empty_list_for_invalid_value(self):
        self.assertListEqual([], lasertag.tags("doesntexist"))


class RenameTagTest(unittest.TestCase):
    def setUp(self):
        test_setup()
        test_populate()

    def test_rename_single_occurrence_tag(self):
        lasertag.rename_tag("host:bank.com", to="host:anotherbank.com")
        self.assertTrue(len(lasertag.query("host:bank.com")) == 0)
        self.assertTrue(len(lasertag.query("host:anotherbank.com")) == 1)

    def test_rename_multi_occurrence_tag(self):
        lasertag.rename_tag("userid:345", to="userid:999")
        self.assertTrue(len(lasertag.query("userid:345")) == 0)
        self.assertTrue(len(lasertag.query("userid:999")) == 2)

    def test_rename_no_occurrence_tag(self):
        lasertag.rename_tag("invalid", to="invalid2")
        self.assertTrue(len(lasertag.query("invalid")) == 0)
        self.assertTrue(len(lasertag.query("invalid2")) == 0)


class ReplaceValueTest(unittest.TestCase):
    def setUp(self):
        test_setup()
        test_populate()

    def test_replace_value(self):
        lasertag.replace_value("image1.jpg", to="image-new.jpg")
        self.assertEquals([], lasertag.tags("image1.jpg"))
        self.assertEquals(["source:http", "userid:123", "type:image"],
                          lasertag.tags("image-new.jpg"))

    def test_replace_no_occurrence_value(self):
        lasertag.replace_value("invalid", to="invalid2")
        self.assertEquals([], lasertag.tags("invalid"))
        self.assertEquals([], lasertag.tags("invalid2"))


if __name__ == "__main__":
    unittest.main()
