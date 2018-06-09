import unittest
from sqlobject import sqlhub

import lasertag


class AddValueTest(unittest.TestCase):
    def setUp(self):
        try:
            conn = sqlhub.getConnection()
            conn.close()
        except AttributeError:
            # Unhelpfully, we receive an `AttributeError` when the connection
            # wasn't estabilished before rather than a return value.
            pass

        lasertag.prepare(lasertag.IN_MEMORY_SQLITE)

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


if __name__ == "__main__":
    unittest.main()
