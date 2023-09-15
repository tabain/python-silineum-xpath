import os
import sys

from lxml import html
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException
import requests
import random

trees = []
options = Options()
options.add_argument("--headless=new")
options.add_argument("--start-maximized")
options.add_argument('--disable-browser-side-navigation')
def get_product_by_url(product_url: str):
    driver = webdriver.Chrome(options=options)

    driver.get(product_url)
    driver.implicitly_wait(random.randrange(6, 10))
    total_page_height = driver.execute_script("return document.body.scrollHeight")
    browser_window_height = driver.get_window_size(windowHandle='current')['height']
    current_position = driver.execute_script('return window.pageYOffset')
    while total_page_height - current_position - 200 > browser_window_height:
        driver.implicitly_wait(random.randrange(1, 2))
        driver.execute_script(f"window.scrollTo({current_position}, {browser_window_height + current_position});")
        current_position = driver.execute_script('return window.pageYOffset')
        driver.implicitly_wait(random.randrange(1, 2))  # It is necessary here to give it some time
    # driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    driver.implicitly_wait(random.randrange(1, 2))
    driver.execute_script('window.scrollTo(0, 0);')
    driver.implicitly_wait(random.randrange(1, 2))
    product_details_tree = html.fromstring(driver.page_source)

    store_name = "".join(product_details_tree.xpath("//a[@class='store-header--storeName--vINzvPw']/text()"))
    if store_name != '':
        store_cred = driver.find_element(By.XPATH, f'//a[text()="{store_name.strip()}"]')
        hover = ActionChains(driver).move_to_element(store_cred)
        hover.perform()
        driver.implicitly_wait(random.randrange(1, 2))
    product_details_tree = html.fromstring(driver.page_source)
    busi_url = product_details_tree.xpath('//a[text()="Business info"]/@href')
    product_id = product_url.split('.html')[0].split('//www.aliexpress.com/item/')[1]
    ratting = ''.join(
        list(dict.fromkeys(product_details_tree.xpath('//span[@class="overview-rating-average"]/text()'))))
    reviews_count = ''.join(
        list(dict.fromkeys(product_details_tree.xpath('//a[@class="product-reviewer-reviews black-link"]/text()'))))
    reviews_comments = []
    if ratting == '':
        ratting = '0'
    if reviews_count == '':
        reviews_count = '0'
    if reviews_count != '0':
        x = requests.get(
            f'https://feedback.aliexpress.com/pc/searchEvaluation.do?productId={product_id}&lang=en_US&page=1&pageSize=100&filter=all&sort=complex_default')
        reviews_comments = x.json()['data']['evaViewList']
    driver.implicitly_wait(random.randrange(5, 10))
    product_title = ''.join(product_details_tree.xpath('//div[@class="title--wrap--Ms9Zv4A"]/h1/text()'))
    product_review_sold = ''.join(product_details_tree.xpath('//span[@class="product-reviewer-sold"]/text()'))
    product_price = ''.join(product_details_tree.xpath(
        '//div[@class="price--current--H7sGzqb product-price-current"]/descendant-or-self::*/text()'))
    product_images = list(dict.fromkeys(product_details_tree.xpath('//img[@class="detail-desc-decorate-image"]/@src')))
    if len(product_images) == 0:
        product_images = list(dict.fromkeys(
            product_details_tree.xpath('//div[@class="detail-desc-decorate-richtext"]/descendant-or-self::*/@src')))
    if len(product_images) == 0:
        product_images = list(dict.fromkeys(
            product_details_tree.xpath('//div[@id="product-description"]/descendant-or-self::*/@src')))
    if len(product_images) == 0:
        product_images = list(dict.fromkeys(
            product_details_tree.xpath('//div[@class="description--origin-part--SsZJoGC"]/descendant-or-self::*/@src')))
    product_description = ''.join(list(
        dict.fromkeys(product_details_tree.xpath('//div[@id="product-description"]/descendant-or-self::*/text()'))))
    if product_description == '':
        product_description = ''.join(list(
            dict.fromkeys(product_details_tree.xpath(
                '//div[@class="detail-desc-decorate-richtext"]/descendant-or-self::*/text()'))))
    sleep(1)
    store_name = ''.join(product_details_tree.xpath('//a[@class="store-header--storeName--vINzvPw"]/text()'))
    store_url = ''.join(product_details_tree.xpath('//a[@class="store-header--storeName--vINzvPw"]/@href'))
    store_id = ''.join(store_url).split('/')[len(''.join(store_url).split('/')) - 1]
    product_colors = list(
        dict.fromkeys(product_details_tree.xpath('//div[@class="sku-item--skus--MmsF8fD"]/div/img/@alt')))
    # ur = ''.join(busi_url)
    # if ur != '':
    #     business_info_capture('https:' + ur)
    # products.insert(0, {
    #     'reviews_comments': reviews_comments,
    #     'product_id': product_id,
    #     'product_title': product_title,
    #     'product_review_sold': product_review_sold,
    #     'product_price': product_price,
    #     'product_images': product_images,
    #     'product_description': product_description,
    #     'store_name': store_name,
    #     'store_url': store_url,
    #     'store_id': store_id,
    #     'product_colors': product_colors,
    #     'ratting': ratting,
    #     'reviews_count': reviews_count
    # })
    product = {
        "product_url": product_url,
        "platform": "ali_express",
        'product_id': product_id,
        'product_title': product_title,
        'product_review_sold': product_review_sold,
        'product_price': product_price,
        'product_images': product_images,
        'product_description': product_description,
        'store_name': store_name,
        'store_url': store_url,
        'store_id': store_id,
        'product_colors': product_colors,
        'ratting': ratting,
        'reviews_count': reviews_count,
        'reviews_comments': reviews_comments,
    }
    driver.close()
    sleep(random.randrange(1, 2))
    return product


    # driver.set_page_load_timeout(30)
    # try:
    #
    # except TimeoutException:
    #     print('Page Timeout')
    #     driver.close()
    #     sleep(1)
        # driver.close()
    # print('Product_Count', len(products))
sys.modules[__name__] = get_product_by_url

