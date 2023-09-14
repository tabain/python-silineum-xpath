import os
import json
import re
from lxml import html
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

import get_all_categories_product
trees = []
options = Options()
options.add_argument("--headless=new")
options.add_argument("--start-maximized")

categories_name_urls = {}

def categories_links():
    driver = webdriver.Chrome(options=options)

    driver.get('https://www.aliexpress.com/')
    tree = html.fromstring(driver.page_source)
    sleep(1)
    for hover_class in tree.xpath('//div[@class="categories-list-box"]/dl/@class'):
        store_cred = driver.find_element(By.XPATH, f'//div[@class="categories-list-box"]/dl[@class="{hover_class}"]')
        hover = ActionChains(driver).move_to_element(store_cred)
        hover.perform()
        driver.implicitly_wait(5)
        sleep(1)
        tree = html.fromstring(driver.page_source)
    for dl in tree.xpath('//div[@class="categories-list-box"]/dl'):
        cat_name = ''.join(dl.xpath('.//*[@class="cate-name"]/span/a/text()')).strip()
        categories_name_urls[cat_name] = []
        # print(cat_name)
        for dd in dl.xpath('.//dl[@class="sub-cate-items"]/dd/a') :
            subcat_name = ''.join(dd.xpath('./text()'))
            subcat_url = ''.join(dd.xpath('./@href'))
            regex_match = re.search("https://", subcat_url)
            if regex_match:
                print('Yes! we have match')
            else :
                subcat_url = 'https:' + subcat_url
                # print(subcat_url)
            categories_name_urls[cat_name].append({'sub_cat': subcat_name, 'url': subcat_url})
        sleep(1)

    # print(categories_name_urls)
    length = 0
    for key in categories_name_urls:
        subs = categories_name_urls[key]
        length += len(subs)
        # print(length)
        # for sub in subs:
        #     print(sub)

    # Data to be written
    with open("json/all_categories.json", "w") as outfile:
        json.dump(categories_name_urls, outfile)
    driver.close()
    sleep(3)
    get_all_categories_product()
    # ()



if __name__ == '__main__':
    categories_links()