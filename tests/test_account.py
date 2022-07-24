import json
import unittest
from tastediveW import auth, Account

class t_account(unittest.TestCase):
    def setUp(self) -> None:
        with open(".json") as f:
            self.json_data = json.load(f)

        auth.setCookies(self.json_data)

    def test_account_get_all_titles(self):
        acc = Account(load_all=True)
        for title in acc.titles:
            break
        
        title.refetch()

        pass

        for x in title.similar:
            print(x)
