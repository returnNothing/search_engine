import mwclient

# Сonnect to a site.
site = mwclient.Site('ru.wiktionary.org')

# Write down all the nouns in the file.
with open('nouns.txt', 'w', encoding='utf_8') as f:
    for page in site.Categories['Русские существительные']:

        # If it's a page and not a category.
        if page.namespace != 14:
            f.write(page.name + '\n')

        # If it's a category.
        else:
            for article in page:
                f.write(article.name + '\n')


