import scrapy
import csv
import json
import re
from html.parser import HTMLParser

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else '' for i in text])

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return '|'.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class HCVID304_www_choppingboard_in_Spider(scrapy.Spider):
    name = "HCVID304.www.choppingboard.in"
    products_seen = []
    jsonData = []

    def closed(self, reason):
        toWrite = {'data' : HCVID304_www_choppingboard_in_Spider.jsonData}
        with open('./json/HCVID304.www.choppingboard.in.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
    
    def start_requests(self):
        url = "http://www.choppingboard.in/"
        yield scrapy.Request(url=url, callback=self.parse)
        
    def parse(self, response):        
        x = response.css('ul#nav > li')        
        for columns in x:
            head_category = columns.css('a span::text').extract_first().strip()
            list_items = columns.css('li.level1')
            for item in list_items:
                page = item.css('a::attr(href)').extract_first()
                sub_category = item.css('a span::text').extract_first().strip()                            
                if page is not None:                    
                    request = scrapy.Request(url= page + '?p=1', callback = self.parsePage)
                    request.meta['pagenum'] = 1
                    request.meta['category'] = str(head_category) + '|' + str(sub_category)
                    yield request

    def parsePage(self, response):
        products = response.css('div.category-products ul.products-grid > li')
        for product in products:
            product_link = product.css('a::attr(href)').extract_first()
            if product_link in HCVID304_www_choppingboard_in_Spider.products_seen:
                return
            else:
                HCVID304_www_choppingboard_in_Spider.products_seen.append(product_link)
            product_image = product.css('img::attr(src)').extract_first()
            product_price = product.css('span.price::text').extract_first().replace('Rs.','')
            request = scrapy.Request(url=product_link, callback=self.parseProduct)
            request.meta['product_link'] = product_link
            request.meta['product_image'] = product_image
            request.meta['product_price'] = product_price
            request.meta['product_category'] = response.meta['category']
            yield request
        nextpage = response.meta['pagenum'] + 1
        product_link = response.request.url[:response.request.url.index('?p=')] + '?p=' + str(nextpage)
        request = scrapy.Request(url=product_link, callback=self.parsePage)
        request.meta['category'] = response.meta['category']
        request.meta['pagenum'] = nextpage
        yield request

    def parseProduct(self, response):
        productLink = response.meta['product_link']
        productCategory = response.meta['product_category']
        productImage = response.meta['product_image']        
        productPrice = response.meta['product_price']

        productName = response.css('div.product-name h1::text').extract_first()
        productDesc = response.css('div.std::text').extract_first().strip()        
        productSku = 'SKU-NA'

        productCategory = productCategory.replace('"','``')        
        productDesc = re.sub('\n' ,'|',productDesc)
        productDesc = re.sub('\t','',productDesc)                             
        productDesc = re.sub('\r','',productDesc)
        productDesc = re.sub('[ ]+',' ',productDesc)
        productDesc = re.sub('(\| )+','|',productDesc)
        productDesc = re.sub('\|+','|',productDesc)
        productDesc = productDesc.strip('|')
        productDesc = productDesc.replace('"','``')
        productName = productName.replace('"','``')

        productDesc = remove_non_ascii(productDesc)        
        productCategory = remove_non_ascii(productCategory)
        productName = remove_non_ascii(productName)

        with open('HCVID304.www.choppingboard.in.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
        
        HCVID304_www_choppingboard_in_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
            
