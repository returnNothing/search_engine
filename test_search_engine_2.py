import unittest
import shelve
import os
from os import remove
import search_engine
import indexer
from indexer import Position_structure
from window import Window


class Test(unittest.TestCase):
# Checks if the method 'many_tokens_search' works right.
    def test_many_tokens_search(self):
        self.maxDiff = None
        text = ['Сегодня мама вымыла 56 рам,', 'поэтому мама очень устала.']

        # Creaction of the test file.
        with open('text.txt', 'w', encoding='UTF-8') as file:
            for i in text:
                file.write(i + '\n')

        # Creation of another test file.
        with open('text2.txt', 'w', encoding='UTF-8') as file2:
            file2.write('Вчера мама тоже устала.')

        # Creation of yet another test file.
        with open('text3.txt', 'w', encoding='UTF-8') as file3:
            file3.write('А завтра мама спит.')

        # Indexation of the test files.
        indexer.Indexer().db_maker('text.txt', 'db')
        indexer.Indexer().db_maker('text2.txt', 'db')
        indexer.Indexer().db_maker('text3.txt', 'db')

        # Checks if 'many_tokens_search' returns a dictionary with right keys and values.
        se = search_engine.Search_Engine(shelve.open('db')).many_tokens_search_2('мама устала', 1, 1)
        self.assertEqual(se, {'text.txt': [Position_structure(0, 8, 11), Position_structure(1, 8, 11),
                            Position_structure(1, 19, 24)], 'text2.txt': [Position_structure(0, 6, 9), Position_structure(0, 16, 21)]})
        del se

        # Checks if 'many_tokens_search' works for one token.
        se2 = search_engine.Search_Engine(shelve.open('db')).many_tokens_search_2('Сегодня', 1, 1)
        self.assertEqual(se2, {'text.txt': [Position_structure(0, 0, 6)]})
        del se2

        # Checks if 'many_tokens_search' returns an empty dictionary if tokens weren't found.
        se3 = search_engine.Search_Engine(shelve.open('db')).many_tokens_search_2('AbCd', 1, 1)
        self.assertEqual(se3, {})
        del se3

        # Checks if 'many_tokens_search' returns an empty dictionary if tokens aren't contained in the same files.
        se4 = search_engine.Search_Engine(shelve.open('db')).many_tokens_search_2('завтра поэтому', 1, 1)
        self.assertEqual(se4, {})
        del se4
        
        # The test files and database are removed.
        os.remove('text.txt')
        os.remove('text2.txt')
        os.remove('text3.txt')
        os.remove('db.bak')
        os.remove('db.dat')
        os.remove('db.dir')

if __name__ == '__main__':
    unittest.main()

