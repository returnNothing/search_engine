"""
This module is used for compiling a database where keys are flexions and values
are tamplates and grammatical categories expressed by those flexions
of Russian nouns from Wiktionary. 
"""

import mwclient
#from time import time
import shelve
import re

#start_time = time()

# Сonnect to the site.
site = mwclient.Site('ru.wiktionary.org')

# A list of inflection templates. 
root = [site.Categories['Шаблоны словоизменений/Существительные/Неодушевлённые/Женский род'],
        site.Categories['Шаблоны словоизменений/Существительные/Неодушевлённые/Мужской род'],
        site.Categories['Шаблоны словоизменений/Существительные/Неодушевлённые/Средний род'],
        site.Categories['Шаблоны словоизменений/Существительные/Одушевлённые/Женский род'],
        site.Categories['Шаблоны словоизменений/Существительные/Одушевлённые/Мужской род'],
        site.Categories['Шаблоны словоизменений/Существительные/Одушевлённые/Средний род']]

# A dict to form a database (keys are flexions,
# values are a list of pairs template name - name of variable with
# grammatical categories).
draft_dict = {}

# A list in case of variation of a flexion. 
flexions = []

# Go through root. 
for category in root:

    # Go through templates in each category. 
    for page in category:

        # Store a template name, cut off 'Шаблон'.
        template = page.name[7:]

        # Store wikitext of the page.  
        page_content = page.text()

        # Split the text. 
        lines = page_content.split('\n')
        for line in lines:

            # Get a val_name (case and number).
            if '={{{основа}}}' in line:
                after_split = line.split('={{{основа}}}')

                # Cut off '|'.
                val_name = after_split[0][1:]

                # Form a pair of template and val_name. 
                pair = (template, val_name)

                # Cut off extra brackets if there is any. 
                flexion = re.sub('[^а-я]', '', (after_split[1]))

            # In case there are more stems than one. 
            elif '={{{основа' in line and \
             line[line.index('а') + 1].isdigit() and \
             line[line.index('а') + 4] == '}':

                after_split = line.split('={{{основа')

                val_name = after_split[0][1:]

                pair = (template, val_name)

                flexion = re.sub('[^а-я]', '', (after_split[1][4:]))

                # In case there is variation of a flexion, store all of them. 
                if 'основа' in flexion:
                    flexions = flexion.split('основа')

                # If there is only one flexion. 
                if flexions == []:
                    draft_dict.setdefault(flexion, []).append(pair)
                    
                else:

                    # If there are multiple choices. 
                    for f in flexions:
                        draft_dict.setdefault(f, []).append(pair)
                    
# The database file is created. 
with shelve.open('noun_flexions_db', 'c') as db:

    # Add a dict in the database. 
    for key in draft_dict:
        db[key] = set(draft_dict[key])

#end_time = time()
#time_taken = end_time - start_time
#print("%s minutes" % (round((time_taken / 60), 2)))
