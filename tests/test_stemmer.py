import unittest
import stemmer

class Tests(unittest.TestCase):

    def setUp(self):
        self.s4 = 'столовая'
        self.stmr = stemmer.Stemmer('flexions.txt')

    # Check if all TypeErrors are raised.
    def test_string(self):
        s = 5
        s2 = ''
        s3 = 'ну'
        with self.assertRaises(TypeError):
            list(self.stmr.pseudostem_generator(s))
        with self.assertRaises(TypeError):
            list(self.stmr.pseudostem_generator(s2))
        with self.assertRaises(TypeError):
            list(self.stmr.pseudostem_generator(s3))
        with self.assertRaises(TypeError):
            list(self.stmr.pseudostem_generator_with_check(s))
        with self.assertRaises(TypeError):
            list(self.stmr.pseudostem_generator_with_check(s2))
        with self.assertRaises(TypeError):
            list(self.stmr.pseudostem_generator_with_check(s3))

    # Check if presudostem_generator yields all pseudostems. 
    def test_pseudostem_generator(self):
        res = self.stmr.pseudostem_generator(self.s4)
        self.assertEqual(list(res), ['столовая', 'столова', 'столов', 'столо'])

    # Check if presudostem_generator yields all pseudostems. 
    def test_pseudostem_generator_with_check(self):
        res = self.stmr.pseudostem_generator_with_check(self.s4)
        self.assertEqual(list(res), ['столовая', 'столова', 'столов'])

if __name__ == '__main__':
    unittest.main()
