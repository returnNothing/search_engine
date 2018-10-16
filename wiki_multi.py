import mwclient
from multiprocessing import Process

site = mwclient.Site('ru.wiktionary.org')

pages = []
stack = [site.Categories['Русские существительные']]

def check_cat(page, pages, stack):

	# Write down all the nouns in the file.
	with open('nouns.txt', 'w', encoding='utf_8') as f:
		if page.namespace != 14:
				pages.append(page)
				f.write(page.name + '\n')
		else:
			stack.insert(0, page)

    return pages
    
while stack:
    cur_node = stack[0]
    stack = stack[1:]       
    for page in cur_node:
        process = Process(target=check_cat, args=(page, pages, stack))
        process.start()
        process.join()
