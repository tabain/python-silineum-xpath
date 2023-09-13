import sys
import json
import category_page


def get_all_categories_product():
    with open("json/all_categories.json", "r") as openfile:
        categories_name_urls = json.load(openfile)

        for key in categories_name_urls:
            subs = categories_name_urls[key]
            for index, sub in enumerate(subs):
                product = category_page(sub['url'])
                subs[index]['product'] = product
                print(index, sub)
            categories_name_urls[key] = subs
            with open("json/all_categories_product.json", "w") as outfile:
                json.dump(categories_name_urls, outfile)



sys.modules[__name__] = get_all_categories_product
