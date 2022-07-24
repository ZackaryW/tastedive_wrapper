from pprint import pprint
import unittest
import json
from tastediveW import MusicTitle, Title, auth

class t_token(unittest.TestCase):
    def setUp(self) -> None:
        with open(".json") as f:
            self.json_data = json.load(f)

    def test_from_cookie(self):
        auth.setCookies(self.json_data)
        self.assertTrue(True)

class t_query(unittest.TestCase):
    def test_similar(self):
        title = Title.getTitle("Cyberpunk-2077")
        pprint(title)
        similars = Title.getSimilar(title)
        
        for s in similars:
            print(str(s))
            self.assertIsInstance(s, Title)
            self.assertIn(title, s.similar)
            
    def test_get_title(self):
        title = Title.getTitle("Cyberpunk-2077")
        self.assertIsInstance(title, Title)
        self.assertEqual(title.slug_name, "cyberpunk-2077")
        self.assertIsInstance(title.similar, tuple)
        self.assertIsNot(0, len(title.similar))

    def test_from_qid(self):
        name = Title.fromQid("B557BCED-AA9F-4B39-BEF7-84802C82ED7D")
        self.assertEqual(name, "Sum-41")

        title = Title.getTitle(name)
        self.assertIsInstance(title, MusicTitle)