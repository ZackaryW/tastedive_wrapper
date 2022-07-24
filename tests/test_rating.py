from pprint import pprint
from time import sleep
import unittest
import json
from tastediveW import Title, auth

class t_rating(unittest.TestCase):
    def setUp(self) -> None:
        with open(".json") as f:
            self.json_data = json.load(f)

        auth.setCookies(self.json_data)

    def test_rating_changes(self):
        title = Title.getTitle("project zomboid")
        rating = title.ratings
        pprint(rating)

        rating.like()
        self.assertTrue(rating.is_like)
        self.assertFalse(rating.is_dislike)
        self.assertFalse(rating.is_meh)
        sleep(1)

        rating.meh()
        self.assertTrue(rating.is_meh)
        self.assertFalse(rating.is_like)
        self.assertFalse(rating.is_dislike)
        sleep(1)

        rating.dislike()
        self.assertTrue(rating.is_dislike)
        self.assertFalse(rating.is_like)
        self.assertFalse(rating.is_meh)
        sleep(1)

        rating.remove_all_lists()
        self.assertTrue(rating.expired)

        rating = title.ratings
        self.assertFalse(rating.expired)

