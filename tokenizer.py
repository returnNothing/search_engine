"""Tokenizer that generates tokens with some of their characteristics.
"""

import unicodedata as u


class Token(object):
    """
    Each token contains 4 attributes. 
    'content' is an alphabetical sequence of a token.
    'first_char_name' is an index of the first letter of the token in the string.
    'last_char_name' is an index of the last letter of the token in the string.
    'length'is length of a token.
    """

    def __init__(self, content, first_char_num):
        self.content = content
        self.first_char_num = first_char_num

    # Calculation of the value of the 'length'-attribute.
    @property
    def length(self):
        return len(self.content)

    # Calculation of the value of 'last_char_num'-attribute.
    @property
    def last_char_num(self):
        return self.first_char_num + self.length - 1


class all_Token(Token):
    """
    Each token contains 5 attributes. 
    'content' is an alphabetical sequence of a token;
    'first_char_name' is an index of the first letter of the token in the string;
    'last_char_name' is an index of the last letter of the token in the string;
    'length' is length of a token;
    'token_type' is a type of the chars a token consists of.
    """

    def __init__(self, content, first_char_num, token_type):
        self.content = content
        self.first_char_num = first_char_num
        self.token_type = token_type


# The class Tokenizer is created. It contains the method 'tokenize',
# which has several realizations.
class Tokenizer(object):
    """
    For tokenization use the class 'Tokenizer' and the method 'tokenize'.
    """

    def tokenize(self, string):
        """
        As a result, the list of Tokens of the typed string is returned.
        """

        # Exception handling if a user typed something that is not a sequence of chars.
        if not isinstance(string, str):
            raise TypeError('This is not a string.')

        # The variable 'has_started' is for indication that the for-loop has started.
        # The variable 'first_char_num' is for 'first_char_num' attribute calculation.
        tokens = []
        has_started = False
        first_char_num = 0

        # The for-loop here is responsible for 'content' attribute filling
        # and calculating the index of the first letter of the token.
        for i, c in enumerate(string):
            if c.isalpha():
                if has_started is False:
                    first_char_num = i
                    has_started = True

            # 'Else' here is responsible for creation of a Token-instance
            # and appending instances of the class 'Token' in the list.
            else:
                has_started = False

                # This instruction checks if only alphabetical Tokens
                # are appended to the list of Tokens.
                if not string[first_char_num:i].isalpha():
                    continue
                tokens.append(Token(string[first_char_num:i], first_char_num))

        # This block is for the case when the last char is alphabetical.
        if has_started and string[-1].isalpha():
            tokens.append(Token(string[first_char_num:i + 1], first_char_num))
        return tokens

    def all_tokenize(self, string):
        """
        As a result, you can get tokens with their characteristics one by one.
        """

        # Exception handling if a user typed something that is not a sequence of chars.
        if not isinstance(string, str):
            raise TypeError('This is not a string.')

        # The variable 'first_char_num' is for 'first_char_num' attribute calculation.
        # The variable 'current_token_type' keeps the type of a token being created.
        first_char_num = 0
        current_token_type = Tokenizer().type_identifier(string[0])

        # The for-loop here is responsible for 'content' attribute filling
        # and calculating the index of the first letter of the token.
        for i, c in enumerate(string):
            if Tokenizer().type_identifier(c) == current_token_type:
                pass

            # 'Else' here is responsible for creation of an all_Token-instance
            # and their yielding. 
            else:
                yield (all_Token(string[first_char_num:i], first_char_num, current_token_type))
                current_token_type = Tokenizer().type_identifier(string[i])
                first_char_num = i

        # This block is for the last char. 
        if string[-1]:
            yield (all_Token(string[first_char_num:i + 1], first_char_num, current_token_type))

    # This method indentifies the type of a token by a type of chars it consist of.
    def type_identifier(self, char):
        if char.isalpha():
            return 'alpha'
        elif char.isdigit():
            return 'digit'
        elif char.isspace():
            return 'space'
        elif u.category(char).startswith('P'):
            return 'punct'
        else:
            return 'other'

    # This method returns only alphabetical and digital tokens for the indexer. 
    def se_tokenize(self, string):
        tokens = Tokenizer().all_tokenize(string)
        for t in tokens:
            if t.token_type == 'alpha' or t.token_type == 'digit':
                yield (t)
