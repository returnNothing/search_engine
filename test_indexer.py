import unittest
import os
from os import remove
import shelve
import indexer
from indexer import Position, Position_for_file, Position_structure


class Tests(unittest.TestCase):
    # Checks if the method 'dict_maker' creates the dictionary right.
    def test_indexer(self):
        d1 = indexer.Indexer().dict_maker('Сегодня мама вымыла 56 рам, поэтому мама очень устала.')

        # Creation of the expected dictionary.
        expected_dict1 = {'Сегодня': [Position(0, 6)], 'мама': [Position(8, 11), Position(36, 39)],
                          'вымыла': [Position(13, 18)], '56': [Position(20, 21)], 'рам': [Position(23, 25)],
                          'поэтому': [Position(28, 34)], 'очень': [Position(41, 45)], 'устала': [Position(47, 52)]}

        # Checks if 'dict_maker' has returned a dictionary instance.
        self.assertIsInstance(d1, dict)

        # Checks if returned dictionary and expected dictionary are equal.
        self.assertDictEqual(d1, expected_dict1)

    # Checks if the method 'dict_maker_for_file' creates a dictionary right.
    def test_indexer_for_file(self):
        text = ['Сегодня мама вымыла 56 рам,', 'поэтому мама очень устала.']

        # Creation of the test file.
        with open('text.txt', 'w', encoding='UTF-8') as file:
            for i in text:
                file.write(i + '\n')

        # Creation of the expected dictionary for 'dict_maker_for_file'.        
        d2 = indexer.Indexer().dict_maker_for_file('text.txt')
        expected_dict2 = {'Сегодня': [Position_for_file('text.txt', 0, 0, 6)],
                          'мама': [Position_for_file('text.txt', 0, 8, 11), Position_for_file('text.txt', 1, 8, 11)],
                          'вымыла': [Position_for_file('text.txt', 0, 13, 18)],
                          '56': [Position_for_file('text.txt', 0, 20, 21)],
                          'рам': [Position_for_file('text.txt', 0, 23, 25)],
                          'поэтому': [Position_for_file('text.txt', 1, 0, 6)],
                          'очень': [Position_for_file('text.txt', 1, 13, 17)],
                          'устала': [Position_for_file('text.txt', 1, 19, 24)]}

        # Checks if 'dict_maker_for_file' has returned a dictionary instance.
        self.assertIsInstance(d2, dict)

        # Checks if returned dictionary and expected dictionary are equal.
        self.assertDictEqual(d2, expected_dict2)

        # Creation of the expected dictionary for 'dict_maker_structure'. 
        d3 = indexer.Indexer().dict_maker_structure('text.txt')
        expected_dict3 = {'Сегодня': {'text.txt': [Position_structure(0, 0, 6)]},
                          'мама': {'text.txt': [Position_structure(0, 8, 11), Position_structure(1, 8, 11)]},
                          'вымыла': {'text.txt': [Position_structure(0, 13, 18)]},
                          '56': {'text.txt': [Position_structure(0, 20, 21)]},
                          'рам': {'text.txt': [Position_structure(0, 23, 25)]},
                          'поэтому': {'text.txt': [Position_structure(1, 0, 6)]},
                          'очень': {'text.txt': [Position_structure(1, 13, 17)]},
                          'устала': {'text.txt': [Position_structure(1, 19, 24)]}}

        # Checks if 'dict_maker_structure' has returned a dictionary instance.
        self.assertIsInstance(d3, dict)

        # Checks if returned dictionary and expected dictionary are equal.
        self.assertDictEqual(d3, expected_dict3)

        # The test file is removed.
        os.remove('text.txt')

    # Checks if the method 'db_maker' creates the database right.
    def test_indexer_for_db(self):
        text = ['Сегодня мама вымыла 56 рам,', 'поэтому мама очень устала.']

        # Creation of the test file.
        with open('text.txt', 'w', encoding='UTF-8') as file:
            for i in text:
                file.write(i + '\n')

        # Creation of another test file.
        with open('text2.txt', 'w', encoding='UTF-8') as file2:
            file2.write('Вчера мама тоже устала.')

        # Creation of the expected dictionary for 'db_maker'.       
        db = indexer.Indexer().db_maker('text.txt', 'db')
        expected_db = {'Сегодня': {'text.txt': [Position_structure(0, 0, 6)]},
                       'мама': {'text.txt': [Position_structure(0, 8, 11), Position_structure(1, 8, 11)]},
                       'вымыла': {'text.txt': [Position_structure(0, 13, 18)]},
                       '56': {'text.txt': [Position_structure(0, 20, 21)]},
                       'рам': {'text.txt': [Position_structure(0, 23, 25)]},
                       'поэтому': {'text.txt': [Position_structure(1, 0, 6)]},
                       'очень': {'text.txt': [Position_structure(1, 13, 17)]},
                       'устала': {'text.txt': [Position_structure(1, 19, 24)]}}

        # Checks if returned database and expected dictionary are equal.
        db = shelve.open('db')
        self.assertDictEqual(dict(db), expected_db)

        # The dabase file is closed.
        db.close()

        # Creation of the expected dictionary for 'db_maker' after indexing one more file.
        db = indexer.Indexer().db_maker('text2.txt', 'db')
        expected_db2 = {'Сегодня': {'text.txt': [Position_structure(0, 0, 6)]},
                        'мама': {'text.txt': [Position_structure(0, 8, 11), Position_structure(1, 8, 11)],
                                 'text2.txt': [Position_structure(0, 6, 9)]},
                        'вымыла': {'text.txt': [Position_structure(0, 13, 18)]},
                        '56': {'text.txt': [Position_structure(0, 20, 21)]},
                        'рам': {'text.txt': [Position_structure(0, 23, 25)]},
                        'поэтому': {'text.txt': [Position_structure(1, 0, 6)]},
                        'очень': {'text.txt': [Position_structure(1, 13, 17)]},
                        'устала': {'text.txt': [Position_structure(1, 19, 24)],
                                   'text2.txt': [Position_structure(0, 16, 21)]},
                        'Вчера': {'text2.txt': [Position_structure(0, 0, 4)]},
                        'тоже': {'text2.txt': [Position_structure(0, 11, 14)]}}

        # Checks if returned database and expected dictionary are equal and tokens of the new file were appended right.
        db = shelve.open('db')   
        self.assertDictEqual(dict(db), expected_db2)

        # The test files are removed and the database file is closed.
        db.close()
        os.remove('text.txt'); os.remove('text2.txt'); os.remove('db.bak'); os.remove('db.dat'); os.remove('db.dir')


if __name__ == '__main__':
    unittest.main()
