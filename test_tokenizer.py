import unittest
import types
import tokenizer


class Tests(unittest.TestCase):

    # Checks if an empty string wasn't typed.
    def test_length(self):
        s = ''
        res = tokenizer.Tokenizer().tokenize(s)
        self.assertEqual(res, [])

    # Checks if token contains all of its chars.
    # Checks if token's length is calculated right.
    # Checks if the first token was created.
    def test_tokenize(self):
        s = 'Мама мыла раму, но забыла про балкон.'
        res = tokenizer.Tokenizer().tokenize(s)
        self.assertEqual(res[0].content, 'Мама')
        self.assertEqual(res[0].length, 4)
        self.assertIsInstance(res[0], tokenizer.Token)
        
    # Checks if the exception raises if a user typed
    # something that is not a sequence of chars.
    def test_type_error(self):
        t = tokenizer.Tokenizer()
        with self.assertRaises(TypeError):
            t.tokenize(5)

    # Checks if 'tokenize' works for the string containing only one token.
    def test_one_token(self):
        s = 'Один'
        res = tokenizer.Tokenizer().tokenize(s)
        self.assertIsInstance(res[0], tokenizer.Token)

    # Checks if non-alphabetical tokens are not created.
    def test_empty_list(self):
        s = '1234567890.'
        res = tokenizer.Tokenizer().tokenize(s)
        self.assertEqual(res, [])

    # Checks if tokens are generated.
    # Checks if token contains all of its chars.
    # Checks if token's length is calculated right.
    # Checks if token's type was identified right.
    # Checks if the first token was created.
    def test_all_tokenize(self):
        s = 'Мама мыла раму, но забыла про балкон.'
        res = tokenizer.Tokenizer().all_tokenize(s)
        self.assertIsInstance(res, types.GeneratorType)
        self.assertEqual(next(res).content, 'Мама')
        self.assertEqual(next(res).length, 1)
        self.assertEqual(next(res).token_type, 'alpha')
        self.assertIsInstance(next(res), tokenizer.all_Token)

    # Checks if the exception raises if a user typed
    # something that is not a sequence of chars.
    def test_type_error_for_all_tokenizer(self):
        t = tokenizer.Tokenizer()
        with self.assertRaises(TypeError):
            list(t.all_tokenize(5))

    # Checks if 'tokenize' works for the string containing only one token.
    def test_one_all_token(self):
        s = 'Один'
        res = tokenizer.Tokenizer().all_tokenize(s)
        self.assertIsInstance(next(res), tokenizer.all_Token)

    # Checks if 'type_identifier' identifies alphabetical chars.
    def test_type_identifier_alpha(self):
        res = tokenizer.Tokenizer().type_identifier('j')
        self.assertEqual(res, 'alpha')

    # Checks if 'type_identifier' identifies digital chars.
    def test_type_identifier_digit(self):
        res = tokenizer.Tokenizer().type_identifier('13')
        self.assertEqual(res, 'digit')

    # Checks if 'type_identifier' identifies different types of spaces.
    def test_type_identifier_space(self):
        res = tokenizer.Tokenizer().type_identifier(' ')
        self.assertEqual(res, 'space')

    # Checks if 'type_identifier' identifies punctuation marks.
    def test_type_identifier_punct(self):
        res = tokenizer.Tokenizer().type_identifier('.')
        self.assertEqual(res, 'punct')

    # Checks if 'type_identifier' identifies other types of chars.
    def test_type_identifier_other(self):
        res = tokenizer.Tokenizer().type_identifier('△')
        self.assertEqual(res, 'other')


if __name__ == '__main__':
    unittest.main()
