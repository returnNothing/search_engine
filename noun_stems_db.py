"""
This module is used for compiling a database where keys are stems and values
are lemmas, tamplates and other stems of Russian nouns from Wiktionary. 
"""

import mwclient
#from time import time
import shelve

#start_time = time()

# Сonnect to the site.
site = mwclient.Site('ru.wiktionary.org')

# The database file is created. 
with shelve.open('noun_stems_db', 'c') as db:

    # The file with nouns is opened.
    with open('nouns.txt', 'r', encoding='utf8') as f:
        
        for word in f:

            # Cut off '\n'. 
            lemma = word[:-1]

            # Find a page of current lemma. 
            page = mwclient.page.Page(site, lemma)

            # Store wikitext of the page. 
            page_content = page.text()

            # Split the text.
            lines = page_content.split('\n')
            for line in lines:

                # A variable to check if there is 'основа1'.
                stem1 = None

                # Get a teplate name, cut the brackets. 
                if '{{сущ ru ' in line:
                    template_name = line[2:]

                # Get a stem.     
                elif '|основа=' in line:

                    # Check if the slot is not empty, and if not,
                    # that a characher after '=' is aphabetical.
                    try:
                        alpha = line[line.index('=') + 1].isalpha()
                    except IndexError:
                        alpha = False

                    if alpha is True:
                        stem = line.split('основа=')[1]

                # Get the second stem if there is one.     
                elif '|основа1=' in line:

                    try:
                        alpha = line[line.index('=') + 1].isalpha()
                    except IndexError:
                        alpha = False

                    if alpha is True:    
                        stem1 = line.split('основа1=')[1]

            # In case there is only one stem.
            if stem1 is None:
                db.setdefault(stem, (lemma, template_name, stem))

            # In case there are two.     
            else:
                db.setdefault(stem, (lemma, template_name, stem, stem1))

#data=shelve.open('noun_stems_db')
#keys = list(data.keys())
#keys.sort()
#for key in keys:
#    print(key, data[key])

#end_time = time()
#time_taken = end_time - start_time
#print("%s minutes" % (round(time_taken / 60), 2))
