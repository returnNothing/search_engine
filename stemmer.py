"""
Stemmer contains a set of functions producing presustems for morphological analysis.
"""

# Добавить док-стринг. 
# The class Stemmer contains two arguments for functions:
# length is the number of symbols a token should contain
# in order to get its pseudoflexions. It's also responsible
# for the maximum number of symbols to cut at the end.
# File stores a text file with a list of flexions of the language.
class Stemmer(object):
    def __init__(self, file = None):

        self.file = file

        # Make a list of flexion from the file.
        with open(self.file, 'r', encoding = 'UTF-8') as f:
            flexions = f.read().split(' ')
            flexions.pop(0)

        self.length = max(len(flex) for flex in flexions)
        self.flexions = set(flexions)

    # presudostem_generator generates 5 pseudostems for each token
    # cutting 0, 1, 2, 3 and 4 symbols from the end respectively. 
    def pseudostem_generator(self, string):
        """
        Use the method 'presudostem_generator' to get 5 pseudostems for your token.
        The first one equals the original token, and four others are that token
        without 1, 2, 3 and 4 symbols at the end respectively.
        """

        # Check, if that the input is str-instance. 
        if not isinstance(string, str):
                raise TypeError('This is not a string.')

        # Check, if it's not empty.
        if string is '':
            raise TypeError('Empty string.')

        # Yield the first pseudoflexion that is equal to the original token.
        yield string

        # If a token is long enough,..
        if len(string) > self.length:

            # ... cut some symbols at the end of it...
            for i in range(1,self.length + 1):

                # ... and yield resulting pseudostems.
                yield string[:-i]

        # If a token is too short, ask for another one.         
        else:
            raise TypeError('The token is too small.')

    # presudostem_generator_with_check generates pseudostems
    # cutting something at the end only if it's a flexion from a set list. 
    def pseudostem_generator_with_check(self, string):
        """
        Use the method 'presudostem_generator_with_check' to get
        only those pseudostems that were obtained by cutting flexions from a set list.
        """

        # Get pseudostems.
        stems = self.pseudostem_generator(string)

        # Yield the first one which equals the original token.
        yield string
            
        while True:

            # Take a stem.
            try:
                stem = next(stems)

            # Check if there is any left.
            except StopIteration:
                raise

            # If a set of symbols in the token after the stem ended
            # equals a flexion from a list,..
            if string[len(stem):] in self.flexions:

                # ... then yield it...
                yield stem

                # ... and do that till all possible pseudostems are obtained
                # cutting flexions from a list from the original token. 
                continue

                # Then take the next one if there is any left. 
                try:
                    stem = next(stems)
                except StopIteration:
                    raise
