import os
import sys
import re

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
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
trees = []
options = Options()
options.add_argument("--headless=new")
options.add_argument("--start-maximized")
options.add_argument('--disable-browser-side-navigation')




def business_info_capture(url: str, driver):
    # driver.set_window_size(800, 1024)
    actions = ActionChains(driver)
    split_str = "&storeNum="
    if len(url.split(split_str)) == 1:
        split_str = "?storeNum="
    name = f'screenshot/{url.split(split_str)[len(url.split(split_str)) - 1]}.png'
    driver.get(url)
    driver.implicitly_wait(5)
    try:
        slide_btn = driver.find_element(By.ID, "nc_1_n1z")
        slide_ctn = driver.find_element(By.ID, "nc_1__scale_text")
        actions.move_to_element(slide_btn).click_and_hold().move_by_offset(slide_ctn.size['width'],0).release().perform()
        driver.implicitly_wait(15)
        print(driver.get_screenshot_as_file(name))
        # return driver.get_screenshot_as_base64()
        return name

    except:
        print(driver.get_screenshot_as_file(name))
        return name
        # return driver.get_screenshot_as_base64()
        # print('System error')
    # sleep(1)
    # os.remove(name)
    # return name

def get_product_by_url(product_url: str):
    license = ''
    driver = webdriver.Chrome(options=options)
    driver.get(product_url)
    driver.implicitly_wait(random.randrange(10, 20))
    total_page_height = driver.execute_script("return document.body.scrollHeight")
    browser_window_height = driver.get_window_size(windowHandle='current')['height']
    current_position = driver.execute_script('return window.pageYOffset')
    while total_page_height - current_position - total_page_height/4 > browser_window_height:
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
            f'https://feedback.aliexpress.com/pc/searchEvaluation.do?productId={product_id}&lang=en_US&page=1&pageSize=10&filter=all&sort=complex_default')
        reviews_comments = x.json()['data']['evaViewList']
    # driver.implicitly_wait(random.randrange(10, 10))
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
    specification = {}
    try:
        c = driver.find_element(By.XPATH, '//*[@id="nav-specification"]/button')
        try:
            c.click()
            driver.implicitly_wait(random.randrange(3, 5))
            product_details_tree = html.fromstring(driver.page_source)
        except WebDriverException:
            print("Element is not clickable")


        for li in product_details_tree.xpath('//*[@id="nav-specification"]/ul/li'):
            for div in li.xpath('.//div'):
                key = ''.join(
                    div.xpath('.//*[@class="specification--title--UbVeyic"]/span/text()')).lower().strip().replace(' ',
                                                                                                                   '_')
                if key != '':
                    specification[key] = ''.join(div.xpath('.//*[@class="specification--desc--Mz148Bl"]/span/text()'))
    except NoSuchElementException:
        for li in product_details_tree.xpath('//*[@id="nav-specification"]/ul/li'):
            for div in li.xpath('.//div'):
                key = ''.join(div.xpath('.//*[@class="specification--title--UbVeyic"]/span/text()')).lower().strip().replace(' ', '_')
                if key != '':
                    specification[key] = ''.join(div.xpath('.//*[@class="specification--desc--Mz148Bl"]/span/text()'))
    print(specification)

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

    # Feedback and store details
    seller_summary = {}
    rating_desc = {}
    feedback_history = []
    metric_prefixes = {
        'T': 1000000000000,
        'G': 1000000000,
        'M': 1000000,
        'K': 1000
    }

    def num_format(num):
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        # add more suffixes if you need them
        return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

    orders = []
    total_items = ''
    if store_id != '':
        store_feedback_url = f'https://www.aliexpress.com/store/feedback-score/{store_id}.html'
        driver.get(store_feedback_url)
        driver.implicitly_wait(5)
        try:
            frame = driver.find_element(By.XPATH ,"//iframe[@id='detail-displayer']")
            driver.switch_to.frame(frame)
        except NoSuchElementException:
            print('No frame')
        feedback_page_tree = html.fromstring(driver.page_source)
        for tr_seller_summary in feedback_page_tree.xpath('//*[@id="feedback-summary"]/*[@class="middle middle-seller"]/table/tbody/tr'):
            key = ''.join(tr_seller_summary.xpath('./th/text()')).replace('(', '_').replace(')', '_').replace(':', '').strip().replace(' ', '_').lower()
            value = ''.join(tr_seller_summary.xpath('./td/descendant-or-self::*/text()'))
            seller_summary[key] = value.strip()
        for tr_seller_rating in feedback_page_tree.xpath('//*[@id="feedback-dsr"]/*[@class="middle middle-seller"]/table/tbody/tr'):
            key = ''.join(tr_seller_rating.xpath('./th/text()')).replace('(', '_').replace(')', '_').replace(':','').strip().replace(' ', '_').lower()
            value = ''.join(tr_seller_rating.xpath('./td/*[@class="dsr-text"]/descendant-or-self::*/text()'))
            value_sec = ''.join(tr_seller_rating.xpath('./td/*[@class="compare-info"]/descendant-or-self::*/text()'))
            rating_desc[key] = f'{value.strip()} {value_sec.strip()}'
        keys = []
        for feedback_key in feedback_page_tree.xpath('//*[@id="feedback-history"]/*[@class="middle"]/table/tbody/*[@class="first"]/*'):
            key = ''.join(feedback_key.xpath('./text()'))
            keys.append(key.strip())

        for feedback_tr in feedback_page_tree.xpath('//*[@id="feedback-history"]/*[@class="middle"]/table/tbody/tr[@class!="first"]'):
            txt_obj = {}
            values_td = feedback_tr.xpath( './*')
            for i in range(len(values_td)):
                # print(i, values_td[i])
                value = ''.join(values_td[i].xpath('./descendant-or-self::*/text()'))
                txt_obj[keys[i]] = value.strip()
            # if idx < len(keys):
            #     txt_obj[keys[idx]] = value.strip()
            feedback_history.append(txt_obj)
        driver.get(f'https://www.aliexpress.com/store/{store_id}/search?SortType=orders_desc')
        driver.implicitly_wait(5)
        all_product_page_tree = html.fromstring(driver.page_source)
        total_items = ''.join(all_product_page_tree.xpath('//*[@class="result-info"]/text()')).strip()
        driver.get(f'https://www.aliexpress.com/store/top-rated-products/{store_id}.html')
        driver.implicitly_wait(5)
        all_product_page_tree = html.fromstring(driver.page_source)

        for li_item in all_product_page_tree.xpath('//ul[@class="items-list util-clearfix"]/li[@class="item"]'):
            sold = ''.join(li_item.xpath('./*[@class="detail"]/*[@class="recent-order"]/text()')).replace('Orders', '').replace('הזמנות', '').replace('Order', '').replace('(', '').replace(')', '').replace(',', '').strip()
            if sold is not '':

                if len(re.findall(r"[^\W\d_]+|\d+", sold)) is not 0:
                    num = 0
                    for z in re.findall(r"[^\W\d_]+|\d+", sold):
                        if z.isdigit():
                            num = int(z)
                        else:
                            print(f'Metric Prefixes {z}')
                            if z in list(metric_prefixes.keys()):
                                print("exist")
                                num = num * metric_prefixes[z]
                    orders.append(num)
                else:
                    orders.append(int(sold))
        ur = ''.join(busi_url)
        if ur != '':
            license = business_info_capture('https:' + ur, driver)






    orders_metric_format = ''
    if len(orders) > 0:
        if sum(orders) > 1000:
            orders_metric_format = num_format(sum(orders))
        else:
            orders_metric_format = str(sum(orders))
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
        'specification': specification,
        'store': {
            'store_feedback': {
                'summary': seller_summary,
                'rating': rating_desc,
                'history': feedback_history
            },
            'store_name': store_name,
            'store_url': store_url,
            'store_id': store_id,
            'sold': orders_metric_format,
            'items': total_items,
            'license_image': license
        },

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

