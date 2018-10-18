"""
This module is used for iterative Depth-first traversal of wikidictionary 
to get all Russian nouns.
"""

import mwclient

# Сonnect to the site.
site = mwclient.Site('ru.wiktionary.org')

# A list for found nouns (~pages in wictionary). 
pages = []

# A list used for Depth-first traversal. 
# Now it contains only a root. 
stack = [site.Categories['Русские существительные']]

# Write down all the nouns in the file.
with open('nouns.txt', 'w', encoding='utf_8') as f:
    
    # Traversing the while tree. 
    while stack:
        
        # Take zero node. 
        cur_node = stack.pop(0)
        
        # Iterate through zero node. 
        for page in cur_node:
            
            # If it's not a category,
            # and it's not already in the list,
            # then add to the final list and write down to the file.
            if page.namespace != 14 and page not in pages:
                pages.append(page)
                f.write(page.name + '\n')
            
            # Otherwise take it as zero node and iterate. 
            else:
                stack.insert(0, page)
        

        

