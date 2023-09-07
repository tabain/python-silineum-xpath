from lxml import html
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import requests
trees = []
options = Options()
# options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)
all_product_href = []
products =[]
def put_text_in_search(text: str):
    driver.get('https://www.aliexpress.com/')
    driver.find_element(By.ID, 'search-key').send_keys(text)
    c = driver.find_element(By.CLASS_NAME, "search-button")
    driver.implicitly_wait(5)
    c.click()
    sleep(1)
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    page()
def page():
    trees.append(html.fromstring(driver.page_source))
    print('Pages{0}'.format(len(trees)))
    tree = html.fromstring(driver.page_source)
    pnf = tree.xpath('//*[@id="root"]/div[1]/div/div/div/div[2]/span[2]/text()')
    if len(pnf) == 0:
        for product_tree in tree.xpath('//div[@id="card-list"]'):
            href = product_tree.xpath('.//a/@href')
            for index, link in enumerate(href):
                if (index % 2) == 0:
                    all_product_href.insert(0, link)
                    get_product(link)
    if len(trees) > 2 :
        exit()

    try:
        c = driver.find_element(By.XPATH, "//li[@class='pagination--paginationLink--2ucXUo6 next-next']")
        if type(c) is 'selenium.webdriver.remote.webelement.WebElement' :
            sleep(5)
            c.click()
            driver.execute_script('window.scrollTo(0, 0);')
            sleep(3)
            driver.execute_script('window.scrollTo(0, 900)')
            page()
    except :
        # handle the exception
        print("No more pages")


def get_product(product_url:str):
    driver.get('https:' + product_url)
    # driver.get(product_url)
    sleep(5)
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    sleep(1)
    product_details_tree = html.fromstring(driver.page_source)
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
    store_name = ''.join(product_details_tree.xpath('//a[@class="store-header--storeName--vINzvPw"]/text()'))
    store_url = ''.join(product_details_tree.xpath('//a[@class="store-header--storeName--vINzvPw"]/@href'))
    store_id = ''.join(store_url).split('/')[len(''.join(store_url).split('/')) - 1]
    product_colors = list(
        dict.fromkeys(product_details_tree.xpath('//div[@class="sku-item--skus--MmsF8fD"]/div/img/@alt')))
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



if __name__ == '__main__':
    # check_ips()
    put_text_in_search('lv designer handbag')



#<li class="brands--item--Po15f9X" clk_trigger="" st_page_id="lawrg6mcxq0caxdj18a60c52b2b77bfc452188cf37" ae_project_id="15210" ae_page_type="list" ae_page_area="middle" ae_button_type="brand_wall" ae_object_type="confirm" data-aplus-clk="x108_aba1622" data-spm-anchor-id="a2g0o.productlist.0.i137.ba776ec8h29Ldi"><img src="//ae01.alicdn.com/kf/HTB1sxUZzIyYBuNkSnfoq6AWgVXa4.jpg_q90.jpg_.webp" alt="" aria-hidden="true"></li>

#https://www.aliexpress.com/w/wholesale-Bike-helmets.html?SearchText=Bike+helmets&catId=0&g=y&initiative_id=SB_20230904071618&spm=a2g0o.productlist.1000002.0&trafficChannel=main&brandValueIds=201299973&isrefine=y