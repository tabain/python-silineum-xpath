import os
import random

from lxml import html
import json

from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import requests
import get_product_by_url

trees = []
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)

all_product_href = []
products =[]
last_url =''
def business_info_capture(url: str):
    driver.set_window_size(600, 900)
    actions = ActionChains(driver)
    split_str = "&storeNum="
    if len(url.split(split_str)) == 1:
        split_str = "?storeNum="
    name = f'screenshot/{url.split(split_str)[len(url.split(split_str)) - 1]}.png'
    driver.get(url)
    sleep(1)

    try:
        slide_btn = driver.find_element(By.ID, "nc_1_n1z")
        slide_ctn = driver.find_element(By.ID, "nc_1__scale_text")
        actions.move_to_element(slide_btn).click_and_hold().move_by_offset(slide_ctn.size['width'],0).release().perform()
        sleep(15)
        print(driver.get_screenshot_as_file(name))
    except:
        print(driver.get_screenshot_as_file(name))
        # print('System error')
    # sleep(1)
    # os.remove(name)
    # return name

def put_text_in_search(text: str):
    wait = WebDriverWait(driver, 5)
    actions = ActionChains(driver)
    driver.get('https://www.aliexpress.com/')
    sleep(2)

    try:
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@style,'display: block')]//img[contains(@src,'TB1')]"))).click()
    except:
        pass

    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, "//img[@class='_24EHh']"))).click()
    except:
        pass
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ship-to"))).click()

    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "shipping-text"))).click()

    ship_to_australia_element = driver.find_element(By.XPATH,
                                                    "//li[@class='address-select-item ']//span[@class='shipping-text' and text()='United Kingdom']")
    actions.move_to_element(ship_to_australia_element).perform()
    sleep(2)
    ship_to_australia_element.click()

    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-role='save']"))).click()
    sleep(2)
    driver.find_element(By.ID, 'search-key').send_keys(text)
    c = driver.find_element(By.CLASS_NAME, "search-button")
    driver.implicitly_wait(5)
    c.click()
    driver.implicitly_wait(5)
    main_tree = html.fromstring(driver.page_source)
    last_url = driver.current_url
    if len(main_tree.xpath('//*[@class="content"]/ul/li/ul/li')) > 0:
        for li in main_tree.xpath('//*[@class="content"]/ul/li/ul/li'):
            category = "".join(li.xpath('.//a/text()')).strip()
            print(category)
            clk_li = driver.find_element(By.XPATH, f'//a[text()="{category}"]')
            driver.implicitly_wait(1)
            clk_li.click()
            driver.implicitly_wait(1)
            # sleep(1)
            page(last_url)
    else:
        page(last_url)
    driver.close()
    sleep(5)
    if len(all_product_href) > 0:
        for href in all_product_href:
            print(href)
            # driver.close()
            product = get_product_by_url(f'https:{href}')
            if product is not None:
                print(f'Product :: {product}')
                with open(f"json/products/25-sep-{text.replace(' ', '-')}-{product['product_id']}.json", "w") as outfile:
                    json.dump(product, outfile)
                with open(f"json/stores/25-sep-{product['store']['store_id']}.json", "w") as outfile:
                    json.dump(product['store'], outfile)
    driver.close()


def page(last_url: str):
    trees.append(html.fromstring(driver.page_source))
    # print('Pages{0}'.format(len(trees)))
    tree = html.fromstring(driver.page_source)
    pnf = tree.xpath('//*[@id="root"]/div[1]/div/div/div/div[2]/span[2]/text()')

    if len(pnf) == 0:
        total_page_height = driver.execute_script("return document.body.scrollHeight")
        browser_window_height = driver.get_window_size(windowHandle='current')['height']
        current_position = driver.execute_script('return window.pageYOffset')
        while total_page_height - current_position - total_page_height/3 > browser_window_height:
            driver.execute_script(f"window.scrollTo({current_position}, {browser_window_height + current_position});")
            current_position = driver.execute_script('return window.pageYOffset')
            sleep(2)  # It is necessary here to give it some time
        # driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        tree = html.fromstring(driver.page_source)
        for product_tree in tree.xpath('//div[@id="card-list"]'):
            href = product_tree.xpath('.//a/@href')
            for index, link in enumerate(href):
                if (index % 2) == 0:
                    all_product_href.insert(0, link)
                    # get_product(link)
    # if len(trees) > 2 :
    #     exit()
    print(f'Urls: {len(all_product_href)}')
    try:
        c = driver.find_element(By.XPATH, "//li[@class='pagination--paginationLink--2ucXUo6 next-next']")
        if c is not None:
            while c is not None:
                driver.implicitly_wait(random.randrange(6, 10))
                c.click()
                driver.execute_script('window.scrollTo(0, 0);')
                driver.implicitly_wait(random.randrange(3, 5))

                page(last_url)
                driver.implicitly_wait(random.randrange(3, 5))
    except :
        # handle the exception
        print("No more pages")
        driver.get(last_url)
        driver.implicitly_wait(random.randrange(3, 5))



def get_product(product_url:str):
    driver.get('https:' + product_url)
    # driver.get(product_url)
    # driver.implicitly_wait(5)
    sleep(1)
    total_page_height = driver.execute_script("return document.body.scrollHeight")
    browser_window_height = driver.get_window_size(windowHandle='current')['height']
    current_position = driver.execute_script('return window.pageYOffset')
    while total_page_height - current_position > browser_window_height:
        driver.execute_script(f"window.scrollTo({current_position}, {browser_window_height + current_position});")
        current_position = driver.execute_script('return window.pageYOffset')
        sleep(1)  # It is necessary here to give it some time
    driver.execute_script('window.scrollTo(0, 0);')

    sleep(1)
    store_cred = driver.find_element(By.CLASS_NAME, 'store-header--storeName--vINzvPw')
    hover = ActionChains(driver).move_to_element(store_cred)
    hover.perform()
    sleep(5)
    product_details_tree = html.fromstring(driver.page_source)
    # sleep(6)
    # driver.find_element(By.)
    busi_url = product_details_tree.xpath('//a[text()="Business info"]/@href')
    product_id = product_url.split('.html')[0].split('//www.aliexpress.com/item/')[1]
    ratting = ''.join(
        list(dict.fromkeys(product_details_tree.xpath('//span[@class="overview-rating-average"]/text()'))))
    reviews_count = ''.join(
        list(dict.fromkeys(product_details_tree.xpath('//a[@class="product-reviewer-reviews black-link"]/text()'))))
    reviews_comments=[]
    if ratting == '':
        ratting = '0'
    if reviews_count == '':
        reviews_count = '0'
    if reviews_count != '0':
        x = requests.get(f'https://feedback.aliexpress.com/pc/searchEvaluation.do?productId={product_id}&lang=en_US&page=1&pageSize=100&filter=all&sort=complex_default')
        reviews_comments = x.json()['data']['evaViewList']
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
    #
    store_name = ''.join(product_details_tree.xpath('//a[@class="store-header--storeName--vINzvPw"]/text()'))

    store_url = ''.join(product_details_tree.xpath('//a[@class="store-header--storeName--vINzvPw"]/@href'))
    store_id = ''.join(store_url).split('/')[len(''.join(store_url).split('/')) - 1]
    product_colors = list(
        dict.fromkeys(product_details_tree.xpath('//div[@class="sku-item--skus--MmsF8fD"]/div/img/@alt')))
    ur = ''.join(busi_url)
    if ur != '':
        business_info_capture('https:'+ur)
    products.insert(0, {
        'reviews_comments': reviews_comments,
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
        'reviews_count': reviews_count
    })
    print({
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

    })
    print('Product_Count', len(products))
    if len(products) == 10:
        exit()



if __name__ == '__main__':
    # check_ips()
    # business_info_capture('https://shoprenderview.aliexpress.com/credential/showcredential.htm?spm=a2g0o.detail.0.0.278a2rCF2rCFGZ&storeNum=1102937457')
    # get_product_by_url("https://www.aliexpress.com/item/1005004580508231.html")
    # get_product_by_url("https://www.aliexpress.com/item/1005005758513030.html?spm=a2g0o.productlist.main.27.1cca49cbNTWXdS&algo_pvid=8e35d312-b219-4e91-ab4c-a0b4ffe3efcd&algo_exp_id=8e35d312-b219-4e91-ab4c-a0b4ffe3efcd-13&pdp_npi=4%40dis%21PKR%213313.39%211723.09%21%21%2182.34%21%21%402101fd4b16954073554711925e6666%2112000034382112176%21sea%21PK%210%21AB&curPageLogUid=ONUueg9efP97")
    put_text_in_search('jacquemus bag')
    # get_product('https://www.aliexpress.com/item/1005005476023158.html?spm=a2g0o.productlist.main.105.25ae2871cuStnG&algo_pvid=85869fde-b8c4-469d-a676-d75ee2ab051c&algo_exp_id=85869fde-b8c4-469d-a676-d75ee2ab051c-53&pdp_npi=4%40dis%21USD%2171.08%2149.76%21%21%21520.00%21%21%402101ea7116941773388317409ef19a%2112000033233759515%21sea%21PK%210%21AS&curPageLogUid=3X9KT6Em5EqI')
    # get_product('//www.aliexpress.com/item/1005005667996824.html?spm=a2g0o.productlist.main.5.33d7bb07ONTvxT&algo_pvid=afd7f546-8d90-4eea-a2ab-0aa1e7571217&algo_exp_id=afd7f546-8d90-4eea-a2ab-0aa1e7571217-2&pdp_npi=4%40dis%21USD%2150.24%2120.11%21%21%21365.91%21%21%402101c5b116940906651848224ef6e8%2112000034386640358%21sea%21PK%210%21AS&curPageLogUid=5Kwb7k61HPS1#nav-review')



#<li class="brands--item--Po15f9X" clk_trigger="" st_page_id="lawrg6mcxq0caxdj18a60c52b2b77bfc452188cf37" ae_project_id="15210" ae_page_type="list" ae_page_area="middle" ae_button_type="brand_wall" ae_object_type="confirm" data-aplus-clk="x108_aba1622" data-spm-anchor-id="a2g0o.productlist.0.i137.ba776ec8h29Ldi"><img src="//ae01.alicdn.com/kf/HTB1sxUZzIyYBuNkSnfoq6AWgVXa4.jpg_q90.jpg_.webp" alt="" aria-hidden="true"></li>

#https://www.aliexpress.com/w/wholesale-Bike-helmets.html?SearchText=Bike+helmets&catId=0&g=y&initiative_id=SB_20230904071618&spm=a2g0o.productlist.1000002.0&trafficChannel=main&brandValueIds=201299973&isrefine=y