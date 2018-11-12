"""
This module is used for compiling a database where keys are stems and values
are lemmas, tamplates and other stems of Russian nouns from Wiktionary. 
"""

import mwclient
#from time import time
import shelve
import threading

#start_time = time()

# Method to form sets of features (stem, template_name, val_name)
def get_features(line, template_name, features):
    # Check if the slot is not empty, and if not,
    # that a characher after '=' is aphabetical.
    try:
        alpha = line[line.index('=') + 1].isalpha()
    except IndexError:
        alpha = False

    if alpha is True:
        after_split = line.split('=')
        val_name = after_split[0][1:]

        # Remove accent character. 
        stem = after_split[1].replace('\u0301', '')
        features.append([stem, template_name, val_name])
        
    return features

# Form a database. 
def db_maker(word, draft_dict):

    # Cut off '\n'. 
    lemma = word[:-1]

    # Find a page of current lemma. 
    page = mwclient.page.Page(site, lemma)

    # Store wikitext of the page. 
    page_content = page.text()

    # Split the text.
    lines = page_content.split('\n')

    # A list of features. 
    features = []

    # A val for template name. 
    template_name = ''
    
    for line in lines:

        # Get a teplate name, cut the brackets. 
        if '{{сущ ru ' in line:
            template_name = line[2:]

        # Get a stem.     
        elif '|основа=' in line:
            features = get_features(line, template_name, features)
                
        # Get the second stem if there is one.     
        elif '|основа' in line:

            # Check that a stem has a number and places into brackets. 
            try:
                digit = line[line.index('а') + 1].isdigit()
                if line[line.index('а') + 2] == '=':
                    brackets = True
            except IndexError:
                brackets = False

            if brackets is True:
                features = get_features(line, template_name, features)

    # Add obtained keys and values to the dict. 
    for feature in features:
        value = (lemma, feature[1], feature[2])
        draft_dict.setdefault(feature[0], set()).add(value)
        
    return draft_dict

# Сonnect to the site.
site = mwclient.Site('ru.wiktionary.org')

# Array of threads.
processes = []

# A dict to form the database. 
draft_dict = {}

# The file with nouns is opened.
with open('nouns.txt', 'r', encoding='utf8') as f:
    
    for word in f:

        # Create a thread. 
        processes.append(threading.Thread(target=db_maker, args=(word, draft_dict)))

        # Complete a dict. 
        draft_dict = db_maker(word, draft_dict)

# Start threads.         
for process in processes:
    process.start()

# Join threads. 
for process in processes:
    process.join()

# The database file is created. 
with shelve.open('noun_stems_db', 'c') as db:
    for key in draft_dict:
        db[key] = set(draft_dict[key])
        print(key, db[key])

#end_time = time()
#time_taken = end_time - start_time
#print("%s minutes" % (round(time_taken / 60), 2))
