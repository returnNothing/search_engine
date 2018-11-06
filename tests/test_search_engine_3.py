import unittest
import os
from os import remove
import search_engine
import indexer
from indexer import Position_structure
from window import Window
from unittest.mock import patch

class Window_mock(Window):
    
    def __init__(self, context='', pos_str=0, pos_start=0, cont_w=0, left=0, right=0, positions=None):
        self.cont_w = cont_w
        self.context = context
        self.pos_start = pos_start
        self.pos_str = pos_str
        self.right = right
        self.left = left
        self.positions = positions
        
class Test(unittest.TestCase):

    def setUp(self):
        
        self.string = 'мама'
        self.window_size = 1
        self.maxDiff = None

        # Creaction of the test files.
        text = ['Сегодня мама вымыла 56 рам,', 'поэтому мама очень устала.']
        with open('text.txt', 'w', encoding='UTF-8') as file:
            for i in text:
                file.write(i + '\n')

        with open('text2.txt', 'w', encoding='UTF-8') as file2:
            file2.write('Вчера мама тоже устала.')

        with open('text3.txt', 'w', encoding='UTF-8') as file3:
            file3.write('А завтра мама спит.')

        with open('text4.txt', 'w', encoding='UTF-8') as file4:
            file4.write('Мама мыла раму, хотя было уже поздно. Однако она решила, что раму нужно домыть. И домыла в итоге.')

        # Indexation of the test files.
        indexer.Indexer().db_maker('text.txt', 'db')
        indexer.Indexer().db_maker('text2.txt', 'db')
        indexer.Indexer().db_maker('text3.txt', 'db')
        indexer.Indexer().db_maker('text4.txt', 'db')

        self.search = search_engine.Search_Engine('db')

    def tearDown(self):
        
        # The test files and database are removed.
        del self.search
        os.remove('text.txt')
        os.remove('text2.txt')
        os.remove('text3.txt')
        os.remove('text4.txt')
        os.remove('db.bak')
        os.remove('db.dat')
        os.remove('db.dir')
  
    # Checks if the method 'many_tokens_search_3' works right.
    # and if all the exceptions were raised.
    def test_many_tokens_search_3(self):

        se = self.search.many_tokens_search_3('мама', 2, 0)

        # Checks limit.  
        self.assertEqual(len(se.keys()), 2)

        # Generator is converted to list. 
        for key in se:
            se[key] = list(se[key])

        # Checks if 'many_tokens_search_3' returns a correct dictionary.
        self.assertEqual(se, {'text.txt': [Position_structure(0, 8, 11), Position_structure(1, 8, 11)],
                              'text2.txt': [Position_structure(0, 6, 9)]})
        del se

        # Checks that if a searched token wasn't found in the database, an empty dictionary is returned.
        se2 = self.search.many_tokens_search_3('AbCd', 1, 0)
        self.assertEqual(se2, {})

        # Checks if TypeError was raised if a user tries to find
        # anything that is not a sequence of chars in the database.
        with self.assertRaises(TypeError):
            self.search.many_tokens_search_3(5, 1, 0)
        del se2

    # Checks if the method 'context_maker' works right.
    def test_context_maker(self):
        
        new_w = self.search.context_maker('text.txt', iter([Position_structure(0, 8, 11),
                                        Position_structure(1, 8, 11)]),
                                        self.window_size)
        
        # Windows are created for obtained positions. 
        self.assertEqual(next(new_w), Window_mock(pos_str=0, left=0, right=18))
        self.assertEqual(next(new_w), Window_mock(pos_str=1, left=0, right=17))

    # Checks if the method 'position_with_context_3' works right.
    def test_position_with_context_3(self):
        
        se = self.search.position_with_context_3(self.string, self.window_size, 1, 1)

        # Checks limit. 
        self.assertEqual(len(se.keys()), 1)

        # Generator is converted to list. 
        for key in se:
            se[key] = list(se[key])

        # Checks if 'position_with_context_3' returns a correct dictionary.
        self.assertEqual(se, {'text2.txt': [Window_mock(pos_str=0, left=0, right=14)]})
        del se

    # Checks if the method 'windows_intersect' works right.    
    def test_windows_intersect(self):
        
        new_w = self.search.windows_intersect(iter([Window_mock(pos_str=0, left=0, right=18,
                                            positions=[Position_structure(0,8,11)]),
                                            Window_mock(pos_str=1, left=0, right=17,
                                            positions=[Position_structure(1,8,11)])]))
        
        # Checks if 'windows_intersect' returns both windows if they do not intersect.
        self.assertEqual(next(new_w), Window_mock(pos_str=0, left=0, right=18,
                                    positions=[Position_structure(0,8,11)]))
        self.assertEqual(next(new_w), Window_mock(pos_str=1, left=0, right=17,
                                    positions=[Position_structure(0,8,11)]))

        # Checks if 'windows_intersect' returns one window if they intersect.
        new_w2 = self.search.windows_intersect(iter([Window_mock(pos_str=0, left=0, right=13,
                                            positions=[Position_structure(0,5,8)]),
                                            Window_mock(pos_str=0, left=5, right=19,
                                            positions=[Position_structure(0,9,13)])]))
        self.assertEqual(next(new_w2), Window_mock(pos_str=0, left=0, right=19,
                                        positions=[Position_structure(0,5,8),Position_structure(0,9,13)]))
        
    # Checks if the method 'context_intersect_3' works right.
    def test_context_intersect_3(self):
        
        se = self.search.context_intersect_3('мыла раму', self.window_size, 1, 0)

        # Checks limit. 
        self.assertEqual(len(se.keys()), 1)

        # Checks if 'context_intersect_3' returns a correct dictionary.
        (se, {'text4.txt': [Window_mock(pos_str=0, left=0, right=19)]})
        del se

    # Checks if the method 'sent_maker' works right.                     
    def test_sent_maker(self):
        
        new_w = self.search.sent_maker(iter([Window_mock(pos_str=0, left=2, right=17,
                                    context='А завтра мама спит.')]))

        # Checks if 'sent_maker' defines the boarders of a sentence correctly.
        self.assertEqual(next(new_w), Window_mock(pos_str=0, left=0, right=18))

    # Checks if the method 'context_sent_3' works right.                     
    def test_context_sent_3(self):
        
        se = self.search.context_sent_3(self.string, self.window_size, 1, 0)

        # Checks limit. 
        self.assertEqual(len(se.keys()), 1)

        # Checks if 'context_sent_3' returns a correct dictionary.
        (se, {'text4.txt': [Window_mock(pos_str=0, left=0, right=17)]})
        del se

    # Checks if the method 'sent_intersect_3' works right.                     
    def test_sent_intersect_3(self):
        
        se = self.search.sent_intersect_3('Однако', self.window_size, 1, 0)

        # Checks limit. 
        self.assertEqual(len(se.keys()), 1)

        # Checks if 'sent_intersect_3' returns a correct dictionary.
        (se, {'text4.txt': [Window_mock(pos_str=0, left=0, right=78)]})
        del se

    # Checks if the method 'emphasize_3' works right.                     
    def test_emphasize_3(self):
        
        se = self.search.emphasize_3('раму', self.window_size, 1, 0, [(0,2)])

        # Checks limit. 
        self.assertEqual(len(se.keys()), 1)

        # Checks if 'emphasize_3' returns a correct dictionary.
        (se, {'text4.txt': ['Мама мыла <b>раму</b>, хотя было уже поздно.', 'Однако она решила, что <b>раму</b> нужно домыть.']})
        del se
               
if __name__ == '__main__':
    unittest.main()
