import os
import json
import re
import sys

from lxml import html
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
trees = []
options = Options()
options.add_argument("--headless=new")
import get_product_by_url
def category_page(url: str):
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    sleep(1)
    driver.refresh()
    sleep(2)
    tree = html.fromstring(driver.page_source)
    pnf = tree.xpath('//*[@id="root"]/div[1]/div/div/div/div[2]/span[2]/text()')
    all_product_href = []
    if len(pnf) == 0:
        for product_tree in tree.xpath('//div[@id="card-list"]'):
            href = product_tree.xpath('.//a/@href')
            for index, link in enumerate(href):
                if (index % 2) == 0:
                    # only one product
                    if len(all_product_href) == 0:
                        all_product_href.append('https:'+link)

        driver.close()
        sleep(1)



        print(all_product_href[0])
        product = get_product_by_url(all_product_href[0])
        return product
    else:
        print('page not found')

sys.modules[__name__] = category_page