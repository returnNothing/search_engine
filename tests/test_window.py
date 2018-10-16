import unittest
import window
import os 

class Test(unittest.TestCase):
    
    def test_position_search(self):
        text = ['Сегодня мама вымыла', 'ну очень много рам, и мама поэтому очень устала.']

        # Creaction of the test file.
        with open('text.txt', 'w', encoding='UTF-8') as file:
            for i in text:
                file.write(i + '\n')

        search = window.Window().position_search('text.txt', 0, 0, 6)
        self.assertEqual(search, 'Сегодня')   
       
        os.remove('text.txt')

if __name__ == '__main__':
    unittest.main()
