import tokenizer
import search_engine
import indexer
from functools import reduce

class Window(object):

    def __init__(self, context='', pos_str=0, pos_start=0, cont_w=0, left=0, right=0, positions=None):
        self.cont_w = cont_w
        self.context = context
        self.pos_start = pos_start
        self.pos_str = pos_str
        self.right = right
        self.left = left
        self.positions = positions

        # If the first char index of a current position equals zero,
        # the left end of a context window also equals zero.
        if self.pos_start == 0:
            self.left = self.pos_start

        # If not, a substring fron the beginning of the string
        # and up to the first char index is sliced. 
        else:
            s1 = self.context[:self.pos_start]
            #print(self.context)

            self.left = 0

            # The substring is tokenized in reversed way.
            for i, t in enumerate(tokenizer.Tokenizer().se_tokenize(s1[::-1])):
                # The left end of the context windows at first equals
                # the last char index of the string and then,
                # if the substring is big enough for a given size of a context window,
                # is calculated.
                if i == self.cont_w - 1:
                    self.left = self.pos_start - t.last_char_num - 1
                    break

        # A substring from a first char index of the current position
        # up till the end of the string is sliced.
        s2 = self.context[self.pos_start:]

        # The substring is tokenized.
        tokens = list(tokenizer.Tokenizer().se_tokenize(s2))
        ######################################################
        if tokens[-1] is '':
            pass
        else:
            self.right = self.pos_start + tokens[-1].last_char_num
        
            for i2, t2 in enumerate(tokens):
                # The right end of the context window is at first equals
                # the last char index of the string and then,
                # if the substring is big enough for a given size of a context window,
                # is calculated.
                if i2 == self.cont_w:
                    self.right = self.pos_start + t2.last_char_num
                    break
                    
    def __repr__(self):
        return '({}, {}, {})'.format(self.pos_str, self.left, self.right)

    def __eq__(self, obj):
        return self.pos_str == obj.pos_str and self.left == obj.left and self.right == obj.right

    #@property
    #def context(self):
    #    return self.context[self.left:self.right + 1]

    def position_search(self, file_name, str_num, start, end):
        result = ''
        with open(file_name, 'r', encoding = 'UTF-8') as f:
            for n, s in enumerate(f):
                if n == str_num:
                    result = s[start:end+1]
        return result

    def intersects(self,window2):
        """
        Checks whether two windows intersect.
        We will need this method for joining windows.
        """
        return self.positions[0].str_num == window2.positions[0].str_num\
               and self.right >= window2.left
