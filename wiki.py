"""
This module is used for iterative Depth-first traversal of wikidictionary 
to get all Russian nouns.
"""

import mwclient
#from time import time

#start_time = time()

# Сonnect to the site.
site = mwclient.Site('ru.wiktionary.org')

# A list used for Depth-first traversal. 
# Now it contains only a root. 
stack = [site.Categories['Русские существительные']]

# To check categories and pages we've visited;
# a list of categories not to traverse.  
bad_stack = set(['Существительные в винительном падеже',
             'Существительные в дательном падеже',
             'Существительные в звательном падеже',
             'Существительные в предложном падеже',
             'Существительные в разделительном падеже',
             'Существительные в родительном падеже',
             'Существительные в творительном падеже'])

# Write down all the nouns in the file.
with open('nouns.txt', 'w', encoding='utf_8') as f:
    
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
                    f.write(page.name + '\n')
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
        
#end_time = time()
#time_taken = end_time - start_time
#print("%s minutes" % (round((time_taken / 60), 2)))
# 7.03 minutes. 
