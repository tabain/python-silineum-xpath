# import random
# import this
from lxml import html
from time import sleep
from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

# from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
all_product_href = []
products =[]


def check_ips():
    for x in range(0, 8):
        options = Options()
        ua = UserAgent()
        user_agent = ua.random
        print(user_agent)
        options.add_argument(f'user-agent={user_agent}')
        driver = webdriver.Chrome(options=options)
        driver.get('https://whoer.net/')
        driver.quit()
def search_by_pages(search_str: str):
    search_text = search_str.strip()
    url = 'https://www.aliexpress.com/w/wholesale-{0}.html?catId=0&SearchText={1}'.format(search_text.replace(' ', '-'), search_text.replace(' ', '+'))
    print(url)
    driver.get(url)
    sleep(1)
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    sleep(1)
    tree = html.fromstring(driver.page_source)
    pnf = tree.xpath('//*[@id="root"]/div[1]/div/div/div/div[2]/span[2]/text()')
    if len(pnf) > 0 :
        driver.refresh()
        sleep(1)
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        sleep(1)
        tree = html.fromstring(driver.page_source)
        pnf = tree.xpath('//*[@id="root"]/div[1]/div/div/div/div[2]/span[2]/text()')
    if len(pnf) == 0:
        page_number = int(tree.xpath('//li[@class="pagination--paginationLink--2ucXUo6"]/text()')[-1])
        for page_nb in range(1, page_number+1):
            driver.get(url+'&page={0}'.format(page_nb))
            sleep(1)
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            sleep(1)
            tree = html.fromstring(driver.page_source)
            page_number = int(tree.xpath('//li[@class="pagination--paginationLink--2ucXUo6"]/text()')[-1])
            for product_tree in tree.xpath('//div[@id="card-list"]'):
                href = product_tree.xpath('.//a/@href')
                for index, link in enumerate(href):
                    if (index % 2) == 0:
                        all_product_href.insert(0, link)
                        # get_product(link)
        print(len(all_product_href))
    else:
        print('Page not found')

def get_product(product_url:str):
    driver.get('https:' + product_url)
    # driver.get(product_url)
    sleep(1)
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    sleep(2)
    product_details_tree = html.fromstring(driver.page_source)
    ratting = ''.join(
        list(dict.fromkeys(product_details_tree.xpath('//span[@class="overview-rating-average"]/text()'))))
    reviews_count = ''.join(
        list(dict.fromkeys(product_details_tree.xpath('//a[@class="product-reviewer-reviews black-link"]/text()'))))
    if ratting == '':
        ratting = '0'
    if reviews_count == '':
        reviews_count = '0'
    product_title = ''.join(product_details_tree.xpath('//div[@class="title--wrap--Ms9Zv4A"]/h1/text()'))
    product_review_sold = ''.join(product_details_tree.xpath('//span[@class="product-reviewer-sold"]/text()'))
    product_price = ''.join(product_details_tree.xpath(
        '//div[@class="es--wrap--erdmPRe notranslate"]/descendant-or-self::*/text()'))
    product_images = list(dict.fromkeys(product_details_tree.xpath('//img[@class="detail-desc-decorate-image"]/@src')))
    if len(product_images) == 0:
        product_images = list(dict.fromkeys(
            product_details_tree.xpath('//div[@class="detail-desc-decorate-richtext"]/descendant-or-self::*/@src')))
    product_description = ''.join(list(
        dict.fromkeys(product_details_tree.xpath('//div[@id="product-description"]/descendant-or-self::*/text()'))))
    if product_description == '':
        product_description = ''.join(list(
            dict.fromkeys(product_details_tree.xpath(
                '//div[@class="detail-desc-decorate-richtext"]/descendant-or-self::*/text()'))))
    store_name = ''.join(product_details_tree.xpath('//a[@class="store-header--storeName--vINzvPw"]/text()'))
    store_url = ''.join(product_details_tree.xpath('//a[@class="store-header--storeName--vINzvPw"]/@href'))
    store_id = ''.join(store_url).split('/')[len(''.join(store_url).split('/')) - 1]
    product_colors = list(
        dict.fromkeys(product_details_tree.xpath('//div[@class="sku-item--skus--MmsF8fD"]/div/img/@alt')))
    products.insert(0, {
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

if __name__ == '__main__':
    # check_ips()
    search_by_pages('Luxury handbags for women')
# print(len(products))


