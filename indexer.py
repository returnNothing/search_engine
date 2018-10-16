"""
Indexer for the search engine.
"""

import tokenizer
import os
import shelve
import functools

# The class 'Position' contains the constructor,
# which keeps information of a token's first and last char index. 
@functools.total_ordering
class Position(object):
    # A 'Position' instance contains 2 attributes,
    # where self.start is the first char index and
    # self.end is the last char index.
    def __init__(self, start, end):
        self.start = start
        self.end = end

    # 'Repr' turns the presentation of 'Position' instance
    # into string.
    def __repr__(self):
        return '({}, {})'.format(self.start, self.end)

    # The method 'eq' is necessary for comparison of the dictionary
    # created by 'dict_maker' and the expected dictionary.
    def __eq__(self, obj):
        return self.start == obj.start and self.end == obj.end

    def __lt__(self, obj):
        if self.str_num != obj.str_num: 
            return self.str_num < obj.str_num
        else:
            return self.start < obj.start

class Position_for_file(Position):
    # A 'Position_for_file' instance contains 4 attributes,
    # where self.file_name is the name of the file a token is in,
    # self.str_num is the number of the string of the file a token is in,
    # self.start is the first char index,
    # self.end is the last char index.
    def __init__(self, file_name, str_num, start, end):
        self.file_name = file_name
        self.str_num = str_num
        self.start = start
        self.end = end

    # 'Repr' turns the presentation of 'Position' instance
    # into string.
    def __repr__(self):
        return '({}, {}, {}, {})'.format(self.file_name, self.str_num, self.start, self.end)

    # The method 'eq' is necessary for comparison of the dictionary
    # created by 'dict_maker' and the expected dictionary.
    def __eq__(self, obj):
        return self.file_name == obj.file_name and self.str_num == obj.str_num and self.start == obj.start and self.end == obj.end


# The class 'Position_structure' contains the constructor,
# which keeps information of token's position in the string of a file it is in
# and its first and last char index.
class Position_structure(Position):
    # A 'Position_structure' instance contains 3 attributes,
    # where self.str_num is the number of the string of the file a token is in,
    # self.start is the first char index,
    # self.end is the last char index.
    def __init__(self, str_num, start, end):
        self.str_num = str_num
        self.start = start
        self.end = end

    # Repr shows all the information as a string.      
    def __repr__(self):
        return '({}, {}, {})'.format(self.str_num, self.start, self.end)

    # The method "eq" is necessary for comparison the result dictionary
    # with actual dictionary in tests.
    def __eq__(self, obj):
        return self.str_num == obj.str_num and self.start == obj.start and self.end == obj.end

# The class 'Indexer' contained different methods
# which indexize different types of data. 
class Indexer(object):

    # 'dict_maker' indexizes the string and returns the dictionary of its tokens.           
    def dict_maker(self, string):
        """
        Use the class 'Indexer' and the method 'dict_maker' to indexize a string.
        """    

        # The string is tokenized and its tokens are appended to the dictionary.
        token = tokenizer.Tokenizer()
        tokens = token.se_tokenize(string)
        dict_of_tokens = {}
        for t in tokens:
            dict_of_tokens.setdefault(t.content, []).append(Position(t.first_char_num, t.last_char_num))
        return dict_of_tokens

    # 'dict_maker_for_file' indexizes the file string by string and returns the dictionary of its tokens.          
    def dict_maker_for_file(self, file):
        """
        Use the class 'Indexer' and the method 'dict_maker_for_file' to indexize a file.
        """
    
        dict_of_tokens = {}

        # The file is opened.
        with open(file, 'r', encoding='UTF-8') as f:

            # The file name is fixed.
            file_name = os.path.basename(file)

            # The file is iterated string by string.
            # Each string is tokenized and its tokens are appended to the dictionary.
            for str_num, string in enumerate(f):
                token = tokenizer.Tokenizer()
                tokens = token.se_tokenize(string)
                for t in tokens:
                    dict_of_tokens.setdefault(t.content, []).append(
                        Position_for_file(file_name, str_num, t.first_char_num, t.last_char_num))
        return dict_of_tokens

    # 'dict_maker_structure' indexizes files string by string and returns the dictionary,
    # where keys are tokens and values are dictionaries containing names of the files
    # a token is in as keys and arrays with information of a number of the string of the file
    # a token is in and its first and last char index.
    def dict_maker_structure(self, file):
        """
        Use the class 'Indexer' and the method 'dict_maker_structure' to indexize a file
        and create the dictionary with a complex structure.
        """
        
        dict_of_tokens = {}

        # The file is opened.
        with open(file, 'r', encoding='UTF-8') as f:

            # The file name is fixed
            file_name = os.path.basename(file)

            # The 'Tokenizer' instance is created.
            token = tokenizer.Tokenizer()

            # The file is iterated string by string.
            # Each string is tokenized and its tokens are appended to the dictionary.
            for str_num, string in enumerate(f):
                tokens = token.se_tokenize(string)
                for t in tokens:
                    dict_of_tokens.setdefault(t.content, {}).setdefault(file_name, []).append(
                        Position_structure(str_num, t.first_char_num, t.last_char_num))
        return dict_of_tokens

    # 'db_maker' indexizes files string by string and returns the database of tokens.       
    def db_maker(self, file, db_name):
        """
        Use the class 'Indexer' and the method 'db_maker' to indexize a file
        and create the database of its tokens.
        """
    
        # The database file is created. 
        with shelve.open(db_name, 'c') as db: 

            # The file is opened.
            with open(file, 'r', encoding='UTF-8') as f:

                # The file name is fixed.
                file_name = os.path.basename(file)

                # The 'Tokenizer' instance is created.
                token = tokenizer.Tokenizer()

                # The file is iterated string by string.
                # Each string is tokenized and its tokens are appended to the database.
                for str_num, string in enumerate(f):
                    tokens = token.se_tokenize(string)
                    for t in tokens:
                        db_tokens = db.setdefault(t.content, {})
                        db_tokens.setdefault(file_name, []).append(
                            Position_structure(str_num, t.first_char_num, t.last_char_num))

                        # As the content of the database was changed, it needs to be rewritten.
                        db[t.content] = db_tokens

#war_and_peace1 = 'C:\\Users\\kanzl\\Google Диск\\Программирование\\Война и мир\\Толстой Лев Николаевич. Война и мир. Том 1.txt'
#war_and_peace2 = 'C:\\Users\\kanzl\\Google Диск\\Программирование\\Война и мир\\Толстой Лев Николаевич. Война и мир. Том 2.txt'
#war_and_peace3 = 'C:\\Users\\kanzl\\Google Диск\\Программирование\\Война и мир\\Толстой Лев Николаевич. Война и мир. Том 3.txt'
#war_and_peace4 = 'C:\\Users\\kanzl\\Google Диск\\Программирование\\Война и мир\\Толстой Лев Николаевич. Война и мир. Том 4.txt'
#db = Indexer().db_maker(war_and_peace1, 'war_and_peace')
#db = Indexer().db_maker(war_and_peace2, 'war_and_peace')
#db = Indexer().db_maker(war_and_peace3, 'war_and_peace')
#db = Indexer().db_maker(war_and_peace4, 'war_and_peace')
