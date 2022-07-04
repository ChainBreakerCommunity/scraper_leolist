import unittest
from dotenv import dotenv_values
import os
config = dotenv_values(".env.test")

class ScraperTesting(unittest.TestCase):

    def test_bot(self):
        os.system("python app.py")

if __name__ == "__main__":
    unittest.main()
