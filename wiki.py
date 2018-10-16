import mwclient

site = mwclient.Site('ru.wiktionary.org')

pages = []
stack = [site.Categories['Русские существительные']]

# Write down all the nouns in the file.
with open('nouns.txt', 'w', encoding='utf_8') as f:
    
    while stack:
        cur_node = stack[0]
        stack = stack[1:]       
        for page in cur_node:
            if page.namespace != 14:
                if page not in pages:
                    pages.append(page)
                    f.write(page.name + '\n')
            else:
                stack.insert(0, page)
        

        

