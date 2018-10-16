import unittest
import os
from os import remove
import search_engine
import indexer
from unittest.mock import patch
import window
from window import Window

class Window_mock(Window):
    
    def __init__(self, file_str='', pos_str=0, pos_start=0, cont_w=0, left=0, right=0):
        self.cont_w = cont_w
        self.file_str = file_str
        self.pos_start = pos_start
        self.pos_str = pos_str
        self.right = right
        self.left = left
        
class Test(unittest.TestCase):
    def test_window(self):
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

         # Creation of yet another test file.
        with open('text4.txt', 'w', encoding='UTF-8') as file4:
            file4.write('Мама мыла раму, хотя было уже поздно. Однако она решила, что раму нужно домыть. И домыла в итоге.')

        # Indexation of the test files.
        indexer.Indexer().db_maker('text.txt', 'db')
        indexer.Indexer().db_maker('text2.txt', 'db')
        indexer.Indexer().db_maker('text3.txt', 'db')
        indexer.Indexer().db_maker('text4.txt', 'db')

        window_1 = search_engine.Search_Engine('db').position_with_context('мама', 2)
        self.assertEqual(window_1, {'text.txt': [Window_mock(pos_str=0, left=0, right=21), Window_mock(pos_str=1, left=0, right=24)], 'text2.txt': [Window_mock(pos_str=0, left=0, right=21)], 'text3.txt': [Window_mock(pos_str=0, left=0, right=17)]})
        del window_1

        window_2 = search_engine.Search_Engine('db').position_with_context('поэтому устала', 2)
        self.assertEqual(window_2, {'text.txt': [Window_mock(pos_str=1, left=0, right=17), Window_mock(pos_str=1, left=8, right=24)]})
        del window_2

        window_3 = search_engine.Search_Engine('db').position_with_context('мама тоже', 2)
        self.assertEqual(window_3, {'text2.txt': [Window_mock(pos_str=0, left=0, right=21), Window_mock(pos_str=0, left=0, right=21)]})
        del window_3

        window_4 = search_engine.Search_Engine('db').position_with_context('Сегодня вымыла', 2)
        self.assertEqual(window_4, {'text.txt': [Window_mock(pos_str=0, left=0, right=18), Window_mock(pos_str=0, left=0, right=25)]})
        del window_4

        #window_5 = search_engine.Search_Engine('db').position_with_context(2, 'мама 56')
        #self.assertEqual(window_5, {'text.txt': [Window_mock(pos_str=0, left=0, right=21), Window_mock(pos_str=0, left=8, right=24)]})
        #del window_5 #Проблема в сортировке.
        #Сортирует значения ключа.
        #Здесь ключ "мама" два раза, поэтому сначала для неё сортировка, потом для "56";
        #думает, что "56" - вторая "мама".
        
        window_6 = search_engine.Search_Engine('db').context_intersect('мама тоже', 2)
        self.assertEqual(window_6, {'text2.txt': [Window_mock(pos_str=0, left=0, right=21)]})
        del window_6

        window_7 = search_engine.Search_Engine('db').context_intersect('Сегодня поэтому', 2)
        self.assertEqual(window_7, {'text.txt': [Window_mock(pos_str=0, left=0, right=18), Window_mock(pos_str=1, left=0, right=17)]})
        del window_7

        window_8 = search_engine.Search_Engine('db').context_intersect('завтра спит', 1)
        self.assertEqual(window_8, {'text3.txt': [Window_mock(pos_str=0, left=0, right=17)]})
        del window_8

        window_9 = search_engine.Search_Engine('db').context_sent('поздно. Однако', 2)
        self.assertEqual(window_9, {'text4.txt': [Window_mock(pos_str=0, left=0, right=78)]})
        del window_9

        window_10 = search_engine.Search_Engine('db').context_sent('Однако', 3)
        self.assertEqual(window_10, {'text4.txt': [Window_mock(pos_str=0, left=0, right=78)]})
        del window_10

        window_11 = search_engine.Search_Engine('db').context_sent('решила', 1)
        self.assertEqual(window_11, {'text4.txt': [Window_mock(pos_str=0, left=38, right=78)]})
        del window_11

        window_12 = search_engine.Search_Engine('db').context_sent('мыла раму', 2)
        self.assertEqual(window_12, {'text4.txt': [Window_mock(pos_str=0, left=0, right=36), Window_mock(pos_str=0, left=38, right=78)]})
        del window_12

        window_13 = search_engine.Search_Engine('db').emphasize('мыла раму', 2)
        self.assertEqual(window_13, {'text4.txt':['Мама <b>мыла</b> <b>раму</b>, хотя было уже поздно.', 'Однако она решила, что <b>раму</b> нужно домыть.']})
        del window_13

        window_14 = search_engine.Search_Engine('db').emphasize('мыла было', 2)
        self.assertEqual(window_14, {'text4.txt': ['Мама <b>мыла</b> раму, хотя <b>было</b> уже поздно.']})
        del window_14

        #window_15 = search_engine.Search_Engine('db').emphasize('Мама мыла раму, хотя было уже поздно', 2)
        #print(window_15)
        #self.assertEqual(window_15, {'text4.txt': ['<b>Мама</b> <b>мыла</b> <b>раму</b>, <b>хотя</b> <b>было</b> <b>уже</b> <b>поздно</b>.', 'Однако она решила, что <b>раму</b> нужно домыть.']})
        #del window_15 
        
        os.remove('text.txt')
        os.remove('text2.txt')
        os.remove('text3.txt')
        os.remove('text4.txt')
        os.remove('db.bak')
        os.remove('db.dat')
        os.remove('db.dir')

if __name__ == '__main__':
    unittest.main()
