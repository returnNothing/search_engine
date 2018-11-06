"""
This module is used for iterative Depth-first multiprocessing traversal of wikidictionary 
to get all Russian nouns.
"""

import mwclient
import threading
#from time import time
import os

#start_time = time()

# Сonnect to the site.
site = mwclient.Site('ru.wiktionary.org')

# A list used for Depth-first traversal. 
# Now it contains only a root. 
root = site.Categories['Русские существительные']

# To check categories and pages we've visited;
# a list of categories not to traverse.  
bad_stack = set(['Существительные в винительном падеже',
             'Существительные в дательном падеже',
             'Существительные в звательном падеже',
             'Существительные в предложном падеже',
             'Существительные в разделительном падеже',
             'Существительные в родительном падеже',
             'Существительные в творительном падеже'])

processes = []

def check_cat(cat, bad_stack, file_name):

    stack = [cat]
    pages = []

    # Write down all the nouns in the file.
    with open(file_name, 'w', encoding='utf_8') as f_2:

        # Traversing the whole tree. 
        while stack:

            # Take zero node. 
            cur_node = stack.pop(0)

            # Iterate through zero node. 
            for page in cur_node:

                # If it's not already in the list,
                # and it's not a category,
                # then add to the final list, write down to the file
                # and remember that we've visited the page.
                if page.name not in bad_stack:
                    if page.namespace != 14:
                        f_2.write(page.name + '\n')
                        bad_stack.add(page.name)

                    else:
                    
                        # In it's a category, take it as zero node and iterate.
                        stack.insert(0, page)
                        
                        # Add category (maybe page) in the set
                        # to remember that we've visited it already.
                        bad_stack.add(cur_node.name)

                # If a page has been visited or shouldn't be traversed,
                # take the next one. 
                else:
                    continue

i = 1
files = ['process_1.txt']

# Write down all the nouns in the file.
with open('process_1.txt', 'w', encoding='utf_8') as f:
        
    # Iterate through zero node. 
    for cat in root:

        if cat.name not in bad_stack:
            if cat.namespace != 14:
                f.write(cat.name + '\n')
                bad_stack.add(cat.name)

            else:
                i+=1
                file_name = 'process_' + str(i) + '.txt'
                files.append(file_name)
                
                # For each cetegory in stack a separate process is created. 
                processes.append(threading.Thread(target=check_cat, args=(cat, bad_stack, file_name))) 
                
for process in processes:
    process.start()

for process in processes:
    process.join()

with open('nouns_2.txt', 'w', encoding='utf_8') as f_3:
    for file in files:
        with open(file, encoding='utf_8') as nouns:
            for line in nouns:
                f_3.write(line)
        os.remove(file)

#end_time = time()
#time_taken = end_time - start_time
#print("%s minutes" % (round((time_taken / 60), 2)))
# 3.84. 
