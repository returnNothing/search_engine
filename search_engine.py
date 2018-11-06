"""
Search Engine contains a set of functions to search in the database.
"""

import shelve
import tokenizer
import window
from functools import reduce
import generator


# The class Search_Engine contains the database to seach in
# and the method, which performs the search. 
class Search_Engine(object):
    def __init__(self, path):

        self.path = path
        self.db = shelve.open(path)

    # Deconstructor for a 'Search_Engine' instance.
    def __del__(self):

        self.db.close()

    # The method 'token_search' returns the value of a seached token in the database.
    def token_search(self, token):
        """
        Use the method 'token_search' to find the requred token.
        """

        # Exception handling if a user tries to find anything that is not a sequense of chars.
        if not isinstance(token, str):
            raise TypeError('This is not a token.')

        # If the searched token wasn't found in the database, an empty dictionaty is returned.
        if token not in self.db:
            return {}

        return self.db[token]

    # The method 'many_tokens_search' returns a dictionary,
    # where keys are file names and values are dictitionaries
    # with tokens and their positions in that file. 
    def many_tokens_search(self, string):
        """
        Use the method 'many_tokens_search' to find phrases and sentences. 
        """

        # The typed string is tokenized.
        tokens = tokenizer.Tokenizer().se_tokenize(string)
        dicts = []
        result = {}

        # All the values of the searched tokens from the database are added into dictionary.
        for t in tokens:
            dicts.append(self.token_search(t.content))

        # The keys of the searched tokens are intersected.
        keys = list(reduce(lambda x, y: x & y.keys(), dicts))

        # The values of the searched tokens are added to the dictionary as long as file names as keys.
        tokens = tokenizer.Tokenizer().se_tokenize(string)
        for token in tokens:
            for key in keys:
                result.setdefault(key, [])

                # 'token_search' returns the dictionary with file names as keys,
                # so it retuns all token's positions in the file.
                result[key].extend(self.token_search(token.content)[key])

        # The values are sorted.           
        for key in result:
            result[key].sort()
        return result

    # The method 'position_with_context' returns a dictionary,
    # where keys are file names and values are arrays of context windows
    # for a query. 
    def position_with_context(self, string, window_size=0):
        """
        Use the method 'position_with_context' to find tokens
        with the required context size.
        """
        windows = {}

        # A dictionary with files and positions for a query is created.
        dict_of_positions = self.many_tokens_search(string)

        # Each file in the dictinary keys is opened.
        for key in dict_of_positions:
            with open(key, 'r', encoding='UTF-8') as f:
                file = enumerate(f)

                # The dictionary values and strings in files are iterated. 
                positions = iter(dict_of_positions[key])

                # Take a string from the file and position from the dictionary. 
                try:
                    current_str_num, current_str = next(file)
                    current_pos = next(positions)
                except StopIteration:
                    raise

                # If a number of a current string in the file is less than
                # a number of the string of a  current position,
                # the next position is taken.
                while True:
                    if current_str_num < current_pos.str_num:

                        # If StopIteration, break. 
                        try:
                            current_str_num, current_str = next(file)
                        except StopIteration:
                            break

                    # If a number of a current string in the file is bigger than
                    # a number of the string of a current position,
                    # the next string is taken.
                    elif current_str_num > current_pos.str_num:

                        # If StopItertion, break.
                        try:
                            current_pos = next(positions)
                        except StopIteration:
                            break

                    # If a number of a current string in the file and
                    # a number of tha string of a current position are equal,
                    # then a Window-instance is created and appended in the dictionary.
                    else:
                        windows.setdefault(key, []).append(
                            window.Window(cont_w=window_size, context=current_str,
                                          pos_str=current_str_num,
                                          pos_start=current_pos.start,
                                          positions=sorted([current_pos])))
                        try:
                            current_pos = next(positions)
                        except StopIteration:
                            break
        return windows

    # The method 'intersect' intersects context windows. 
    def intersect(self, windows):

        for key in windows:
            i = 0
            windows_list = windows[key]

            # Each windows is compared with the next one.
            while i < len(windows_list) - 1:

                # If they intersect...
                if windows_list[i].intersects(windows_list[i + 1]):

                    # ... and are not equal...
                    if windows_list[i] != windows_list[i + 1]:

                        # ... a new window is not created, but rather arguments of
                        # windows_list[i] are changed and windows_list[i+1] is deleted.
                        windows_list[i].positions += windows_list[i + 1].positions

                        # The right border of the window is expended.
                        windows_list[i].right = windows_list[i + 1].right

                        # Windows_list[i+1] is deleted.
                        windows_list.pop(i + 1)

                        # At the next step windows_list[i] with
                        # windows_list[i+1] are compared again, so "i" is not increased.
                        continue

                    # If two windows are equal, the first one is deleted.
                    else:
                        windows_list.pop(i)

                # If windows do not intersect, they both stay in the dictionary as they are.        
                else:
                    i += 1
        return windows

    # The method 'context_sent' expands context window up to the sentence borders.            
    def context_sent(self, string, window_size=0):
        """
        Use the method 'context_sent' to expends windows'
        borders up to the sentences' borders which contain those windows.
        """

        result = {}

        # 'dict_of_windows' is a dictionary where keys are file names and values are context windows.
        dict_of_windows = self.position_with_context(string, window_size)

        # 'windows' contains the same dictionary, but windows are intersected.
        windows = self.intersect(dict_of_windows)

        # The values of each key are iterated.
        for key in windows:
            for p in windows[key]:
                s = p.context[::-1]

                # Each character in a string is checked for the following conditions.
                for i, c in enumerate(s):

                    # The left border is determined as an upper-registered character after space character
                    # and some final punctuation mark before that.
                    try:

                        if (len(s) - 1 - p.left) < i and c.isupper() \
                                and s[i + 1] in {' ', '\n', '\r'} and s[i + 2] in {'.', '!', '?'}:
                            p.left = len(s) - i - 1
                            break

                    except IndexError:
                        p.left = 0
                        break

                s2 = p.context

                for i2, c2 in enumerate(s2):
                    # The right border is determined as any final mark placed
                    # after the primary right border of the window.
                    try:
                        if p.right < i2 and c2 in {'.', '!', '?'} \
                                and s2[i2 + 1] in {' ', '\n', '\r'}:
                            p.right = i2
                            break

                        elif p.right < i2 and c2 in {'.', '!', '?'} \
                                and s2[i2 + 1] in {'.', '!', '?'} and s2[i2 + 2] in {' ', '\n', '\r'}:
                            p.right = i2 + 1
                            break

                        elif p.right < i2 and c2 in {'.', '!', '?'} \
                                and s2[i2 + 1] in {'.', '!', '?'} and s2[i2 + 2] in {'.', '!', '?'}:
                            p.right = i2 + 2
                            break

                            # Otherwise the right border equals the last character in the string.
                    except IndexError:
                        p.right = i2
                        break

                result.setdefault(key, []).append(p)
        return result

    # The method 'emphasize' returns a dictionary, where keys are file names
    # and values are citations containing searched tokens.
    def emphasize(self, string, window_size=0):
        """
        Use the method 'emphasize' to get a list of citations relevant to the query
        and mark searched tokens with bold.
        """

        # 'dict_of_windows' contains sentences.
        dict_of_windows = context_sent(self, string, window_size)

        # Then they're intersected. 
        windows = self.intersect(dict_of_windows)

        final_dict = {}
        for key in windows:
            citations = []
            for w in windows[key]:

                # 'w.positions' contains positions of the searched tokens to mark them in bold.
                for i, p in enumerate(w.positions):
                    if i == 0:

                        # The part from the beginning to the end of the first query word.
                        citation = w.context[w.left:p.start] + "<b>" \
                                   + w.context[p.start:p.end + 1] + "</b>"
                    else:

                        # The part from where it's stopped till the end of the next query word.
                        citation += w.context[w.positions[i - 1].end + 1:p.start] \
                                    + "<b>" + w.context[p.start:p.end + 1] + "</b>"
                    if i == len(w.positions) - 1:
                        # The part from where it's stopped till the end.
                        citation += w.context[p.end + 1:w.right + 1]

                # List of citations.    
                citations.append(citation)

            # A dictionary where keya are file names
            # and values are citations with searched tokens.    
            final_dict[key] = citations
        return final_dict

    # From here begins a new version of Search_Engine, where a user can regulate a number
    # of items they want to see.

    # The method 'many_tokens_search_2' returns a dictionary,
    # where keys are file names and values are dictionaries
    # with tokens and their positions in that file.
    # Parameters 'limit' and 'offset' limit the number of documents in the output.
    def many_tokens_search_2(self, string, limit, offset):
        """
        Use the method 'many_tokens_search_2' to find phrases and sentences.
        Using 'limit' and 'offset' you can limit the number of documents you'd like to see.
        'offset' is the number of the first document you'd like to see.
        'limit' is a number of documents you'd loke to see. 
        """

        # The typed string is tokenized.
        tokens = tokenizer.Tokenizer().se_tokenize(string)
        dicts = []
        result = {}

        # All the values of the searched tokens from the database are added into dictionary.
        for t in tokens:
            dicts.append(self.token_search(t.content))

        # The keys of the searched tokens are intersected...
        keys = list(reduce(lambda x, y: x & y.keys(), dicts))

        # ... sorted...
        keys.sort()

        # ... and limited by the set user perameters.
        limited_keys = keys[offset:offset + limit]

        # The values of the searched tokens are added to the dictionary as long as file names as keys.
        tokens = tokenizer.Tokenizer().se_tokenize(string)
        for token in tokens:
            for key in limited_keys:
                result.setdefault(key, [])

                # 'token_search' returns the dictionary with file names as keys,
                # so it retuns all token's positions in the file.
                result[key].extend(self.token_search(token.content)[key])

        # The values are sorted.          
        for key in result:
            result[key].sort()

        return result

    # The method 'position_with_context_2' returns a dictionary,
    # where keys are file names and values are arrays of context windows
    # for a query.
    def position_with_context_2(self, string, window_size, limit, offset):
        """
        Use the method 'position_with_context_2' to find tokens
        with the required context size.
        """

        windows = {}

        # A dictionary with files and positions for a query is created.
        dict_of_positions = self.many_tokens_search_2(string, limit, offset)

        # Each file in the dictinary keys is opened.
        for key in dict_of_positions:
            with open(key, 'r', encoding='UTF-8') as f:
                file = enumerate(f)

                # The dictionary values and strings in files are iterated.
                iter_positions = iter(dict_of_positions[key])

                # Take a string from the file and position from the dictionary.
                try:
                    current_str_num, current_str = next(file)
                    current_pos = next(iter_positions)
                except StopIteration:
                    raise

                # If a number of a current string in the file is less than
                # a number of the string of a  current position,
                # the next position is taken.
                while True:
                    if current_str_num < current_pos.str_num:

                        try:
                            current_str_num, current_str = next(file)
                        except StopIteration:
                            break

                    elif current_str_num > current_pos.str_num:

                        # If StopIteration, break. 
                        try:
                            current_pos = next(iter_positions)
                        except StopIteration:
                            break

                    # If a number of a current string in the file and
                    # a number of tha string of a current position are equal,
                    # then a Window-instance is created and appended in the dictionary.    
                    else:
                        windows.setdefault(key, []).append(
                            window.Window(cont_w=window_size, context=current_str,
                                          pos_str=current_str_num,
                                          pos_start=current_pos.start,
                                          positions=sorted([current_pos])))
                        try:
                            current_pos = next(iter_positions)
                        except StopIteration:
                            break
        return windows

    # The method 'context_sent_2' returns a dictionary,
    # where keys are file names and values are windows
    # expended up to sentence borders.
    def context_sent_2(self, string, window_size, limit, offset):
        """
        Use the method 'context_sent_2' to expends windows'
        borders up to the sentences' borders which contain those windows.
        """

        result = {}

        # 'dict_of_windows' is a dictionary where keys are file names and values are context windows.
        dict_of_windows = self.position_with_context_2(string, window_size, limit, offset)

        # 'windows' contains the same dictionary, but windows are intersected.
        windows = self.intersect(dict_of_windows)

        # The values of each key are iterated.
        for key in windows:
            for p in windows[key]:
                s = p.context[::-1]

                # Each character in a string is checked for the following conditions.
                for i, c in enumerate(s):

                    # The left border is determined as an upper-registered character
                    # after space character and some final punctuation mark before that.
                    try:

                        if (len(s) - 1 - p.left) < i and c.isupper() \
                                and s[i + 1] in {' ', '\n', '\r'} and s[i + 2] in {'.', '!', '?'}:
                            p.left = len(s) - i - 1
                            break

                    # Otherwise the left border equals the first character in the string.           
                    except IndexError:
                        p.left = 0
                        break

                s2 = p.context

                # The right border is determined as any final mark
                # placed after the primary right border of the window.
                for i2, c2 in enumerate(s2):
                    try:
                        if p.right < i2 and c2 in {'.', '!', '?'} \
                                and s2[i2 + 1] in {' ', '\n', '\r'}:
                            p.right = i2
                            break

                        elif p.right < i2 and c2 in {'.', '!', '?'} \
                                and s2[i2 + 1] in {'.', '!', '?'} and s2[i2 + 2] in {' ', '\n', '\r'}:
                            p.right = i2 + 1
                            break

                        elif p.right < i2 and c2 in {'.', '!', '?'} \
                                and s2[i2 + 1] in {'.', '!', '?'} and s2[i2 + 2] in {'.', '!', '?'}:
                            p.right = i2 + 2
                            break

                    # Otherwise the right border equals the last character in the string.
                    except IndexError:
                        p.right = i2
                        break

                result.setdefault(key, []).append(p)
        return result

    # The method 'emphasize_2' returns a dictionary, where keys are file names
    # and values are citations containing searched tokens.
    # Parameter 'limit_and_offset' limit the number of citations in the output.
    def emphasize_2(self, string, window_size, limit, offset, limit_and_offset):
        """
        Use the method 'many_tokens_search_2' to find phrases and sentences.
        Using 'limit' and 'offset' you can limit the number of citations you'd like to see.
        'limit_and_offset' is a pair, where 'offset' is the number of the first citation
        in the document you'd like to see and 'limit' is a number of citations of the document
        you'd like to see.
        """

        # 'dict_of_windows' contains sentences.
        dict_of_windows = self.context_sent_2(string, window_size, limit, offset)

        # Then they're intersected. 
        windows = self.intersect(dict_of_windows)
        final_dict = {}
        n = 0

        # The number if citations is limited according to set user parameters.
        for key in sorted(windows):

            # Array for citations.    
            citations = []

            # If a user determened the parameters, citations are limited according to them.
            try:
                windows[key] = windows[key][limit_and_offset[n][0]:limit_and_offset[n][0] + limit_and_offset[n][1]]
                n = n + 1

            # If not or not for every document, the defeault pair is (0, 10). 
            except IndexError:
                windows[key] = windows[key][0:10]

            for w in windows[key]:

                # 'w.positions' contains positions of the searched tokens to mark them in bold.
                for i, p in enumerate(w.positions):
                    if i == 0:

                        # The part from the beginning to the end of the first query word.
                        citation = w.context[w.left:p.start] + "<b>" \
                                   + w.context[p.start:p.end + 1] + "</b>"

                    else:

                        # The part from where it's stopped till the end of the next query word.
                        citation += w.context[w.positions[i - 1].end + 1:p.start] \
                                    + "<b>" + w.context[p.start:p.end + 1] + "</b>"

                    if i == len(w.positions) - 1:
                        # The part from where it's stopped till the end.
                        citation += w.context[p.end + 1:w.right + 1]

                # List of citations.    
                citations.append(citation)

            # A dictionary where keya are file names and values are citations with searched tokens.    
            final_dict[key] = citations

        return final_dict

    # From here begins a new version of Search_Engine, where a user can regulate a number
    # of items they want to see and every array is changed to a generator to accelerate  the process.

    # The method 'many_tokens_search_3' returns a dictionary,
    # where keys are file names and values are generators
    # yeilding  positions of in that file.
    # Parameters 'limit' and 'offset' limit the number of documents in the output.
    def many_tokens_search_3(self, string, limit, offset):
        """
        Use the method 'many_tokens_search_3' to find phrases and sentences.
        Using 'limit' and 'offset' you can limit the number of documents you'd like to see.
        'offset' is the number of the first document you'd like to see.
        'limit' is a number of documents you'd like to see. 
        """

        # The typed string is tokenized.
        tokens = tokenizer.Tokenizer().se_tokenize(string)
        dicts = []
        result = {}

        # All the values of the searched tokens from the database are added into dictionary.
        for t in tokens:
            dicts.append(self.token_search(t.content))

        # The keys of the searched tokens are intersected...
        keys = list(reduce(lambda x, y: x & y.keys(), dicts))

        # ... sorted...
        keys.sort()

        # ... and limited by the set user perameters.
        limited_keys = keys[offset:offset + limit]

        # The values are added to the list.
        tokens = list(tokenizer.Tokenizer().se_tokenize(string))
        for key in limited_keys:
            lst_of_positions = []
            for token in tokens:
                # 'token_search' returns the dictionary with file names as keys,
                # so it retuns all token's positions in the file.
                lst_of_positions.append(self.token_search(token.content)[key])

            # 'sorting' is a generator yielding in ascending order one file position at a time.
            result[key] = generator.sorting(lst_of_positions)

        return result

    # The method 'context_maker' is a generator which yields a token with the set context size.
    def context_maker(self, key, positions_lst, window_size):

        # Each file in the dictionary keys is opened.
        with open(key, 'r', encoding='UTF-8') as f:
            file = enumerate(f)

            # Take a string from the file and generate a position. 
            try:
                current_str_num, current_str = next(file)
                current_pos = next(positions_lst)

            except StopIteration:
                raise

            # If a number of a current string in the file is less than
            # a number of the string of a  current position,
            # the next position is taken.
            while True:

                if current_str_num < current_pos.str_num:

                    try:
                        current_str_num, current_str = next(file)
                    except StopIteration:
                        break

                elif current_str_num > current_pos.str_num:

                    # If StopIteration, break.
                    try:
                        current_pos = next(positions_lst)
                    except StopIteration:
                        break

                # If a number of a current string in the file and
                # a number of the string of a current position are equal,
                # then a Window-instance is created and yielded.    
                else:
                    yield window.Window(cont_w=window_size, context=current_str,
                                        pos_str=current_str_num, pos_start=current_pos.start,
                                        positions=sorted([current_pos]))

                    try:
                        current_pos = next(positions_lst)
                    except StopIteration:
                        break

    # The method 'position_with_context_3' returns a dictionary,
    # where keys are file names and values are generators of context windows
    # for a query.
    def position_with_context_3(self, string, window_size, limit, offset):
        """
        Use the method 'position_with_context_2' to find tokens
        with the required context size.
        """

        # A dictionary with files and positions for a query is created.
        dict_of_positions = self.many_tokens_search_3(string, limit, offset)

        # For each document as a value a generator is set. It yields context windows.
        for key in dict_of_positions:
            dict_of_positions[key] = self.context_maker(key, dict_of_positions[key], window_size)

        return dict_of_positions

    # The method 'windows_intersect' intersects context windows. 
    def windows_intersect(self, windows_lst):

        # Each window is compared with the next one.
        try:
            window = next(windows_lst)
            window_2 = next(windows_lst)
        except StopIteration:
            raise

        while True:
            # If they intersect...
            if window.intersects(window_2):

                # ... and not equal,.. 
                if window != window_2:

                    # ... a new window is not created, but rather arguments of
                    # a current window are changed.
                    window.positions += window_2.positions

                    # The right border of the window is expended.
                    window.right = window_2.right

                    try:

                        # The next window is taken to compare. 
                        window_2 = next(windows_lst)

                    except StopIteration:
                        yield window
                        break

                # If windows are the same, leave only one,..
                else:
                    window = window_2

                    # ... and take the next to compare.
                    try:
                        window_2 = next(windows_lst)
                    except StopIteration:
                        yield window
                        break

            # If windows do not intersect, the current one is yielded and the next one
            # is compared with the next if it exists.
            else:
                yield window
                window = window_2

                try:
                    window_2 = next(windows_lst)
                except StopIteration:
                    yield window
                    break

    # The method 'context_intersect_3' returns a dictionary, where
    # keys are file names and values are generators yielding
    # context windows after they have been intersected. 
    def context_intersect_3(self, string, window_size, limit, offset):

        # A dictionary of context windows. 
        windows = self.position_with_context_3(string, window_size, limit, offset)

        # The intersection of windows. 
        for key in windows:
            windows[key] = self.windows_intersect(windows[key])

        return windows

    # The method 'sent_maker' is a generator which yields a window
    # whose borders are expended up to the sentences borders contaning that window.
    def sent_maker(self, windows_lst):

        while True:
            try:
                p = next(windows_lst)
            except StopIteration:
                break

            s = p.context[::-1]

            # Each character in a string is checked for the following conditions.        
            for i, c in enumerate(s):

                # The left border is determined as an upper-registered character
                # after space character and some final punctuation mark before that.
                try:
                    if (len(s) - 1 - p.left) < i and c.isupper() \
                            and s[i + 1] in {' ', '\n', '\r'} and s[i + 2] in {'.', '!', '?'}:
                        p.left = len(s) - i - 1
                        break

                # Otherwise the left border equals the first character in the string.           
                except IndexError:
                    p.left = 0
                    break

            s2 = p.context

            for i2, c2 in enumerate(s2):

                # The right border is determined as any final mark
                # placed after the primary right border of the window.     
                try:
                    if p.right < i2 and c2 in {'.', '!', '?'} \
                            and s2[i2 + 1] in {' ', '\n', '\r'}:
                        p.right = i2
                        break

                    elif p.right < i2 and c2 in {'.', '!', '?'} \
                            and s2[i2 + 1] in {'.', '!', '?'} and s2[i2 + 2] in {' ', '\n', '\r'}:
                        p.right = i2 + 1
                        break

                    elif p.right < i2 and c2 in {'.', '!', '?'} \
                            and s2[i2 + 1] in {'.', '!', '?'} and s2[i2 + 2] in {'.', '!', '?'}:
                        p.right = i2 + 2
                        break

                # Otherwise the right border equals the last character in the string.
                except IndexError:
                    p.right = i2
                    break
            yield p

    # The method 'context_sent_3' returns a dictionary, where
    # keys are file names and values are generator yielding
    # sentences.    
    def context_sent_3(self, string, window_size, limit, offset):
        """
        Use the method 'context_sent_3' to expends windows'
        borders up to the sentences' borders which contain those windows.
        """

        # A dictionary of intersected windows. 
        windows = self.context_intersect_3(string, window_size, limit, offset)

        for key in windows:
            # The borders of each window are expended
            # up to the sentence's borders which contains this window.
            windows[key] = self.sent_maker(windows[key])

        return windows

    # The method 'sent_intersect_3' returns a dictionary, where
    # keys are file names and values are generator yielding
    # intersected sentences. 
    def sent_intersect_3(self, string, window_size, limit, offset):

        # A dictionary with sentences.
        windows = self.context_sent_3(string, window_size, limit, offset)

        # Then they are intersected. 
        for key in windows:
            windows[key] = self.windows_intersect(windows[key])

        return windows

    # The method 'emphasize_3' returns a dictionary, where keys are file names
    # and values are generators of citations containing searched tokens.
    def emphasize_3(self, string, window_size, limit, offset, limit_and_offset):
        """
        Use the method 'emphasize' to get a list of citations relevant to the query
        and mark searched tokens with bold.
        """

        # A dictionary with intersected sentences. 
        windows = self.sent_intersect_3(string, window_size, limit, offset)

        # Count for documents.
        d = 0

        for key in sorted(windows):

            # List for citations of particular document.
            citations = []

            # Count for offset.
            off = 0

            # Count for limit.
            lim = 0

            # Offset for citations of thw document d.
            citations_offset = limit_and_offset[d][0]

            # Limit for citations of thw document d.
            citations_limit = limit_and_offset[d][1]
            d = d + 1

            # Skip until offset. 
            while off < citations_offset:
                try:
                    w = next(windows[key])
                    off += 1
                except StopIteration:
                    break

            else:

                # Make limit citations. 
                while lim < citations_limit:
                    try:
                        w = next(windows[key])
                    except StopIteration:
                        break

                    # 'w.positions' contains positions of the searched tokens to mark them in bold.
                    for i, p in enumerate(w.positions):
                        if i == 0:

                            # The part from the beginning to the end of the first query word.
                            citation = w.context[w.left:p.start] + "<b>" \
                                       + w.context[p.start:p.end + 1] + "</b>"
                        else:

                            # The part from where it's stopped till the end of the next query word.
                            citation += w.context[w.positions[i - 1].end + 1:p.start] \
                                        + "<b>" + w.context[p.start:p.end + 1] + "</b>"

                        # The part from where it's stopped till the end.
                        if i == len(w.positions) - 1:
                            citation += w.context[p.end + 1:w.right + 1]

                    lim += 1

                    citations.append(citation)

            # Replace generator with list of citations.
            windows[key] = citations

        return windows
