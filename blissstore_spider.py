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

class HCVID322_www_blissstore_in_Spider(scrapy.Spider):
    name = "HCVID322.www.blissstore.in"
    products_seen = []
    jsonData = []

    def closed(self, reason):
        toWrite = {'data' : HCVID322_www_blissstore_in_Spider.jsonData}
        with open('./json/HCVID322.www.blissstore.in.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
    
    def start_requests(self):
        page = 'http://www.blissstore.in/collections/bags'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Bags'
        request.meta['pageno'] = 1
        yield request
        page = 'http://www.blissstore.in/collections/bar-accessories'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Bar Accessories'
        request.meta['pageno'] = 1
        yield request
        page = 'http://www.blissstore.in/collections/decor-wall-art'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Decor & Wall Art'
        request.meta['pageno'] = 1
        yield request
        page = 'http://www.blissstore.in/collections/kitchen-dining'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Kitchen & Dining'
        request.meta['pageno'] = 1
        yield request
        page = 'http://www.blissstore.in/collections/stationary'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Stationary'
        request.meta['pageno'] = 1
        yield request
        page = 'http://www.blissstore.in/collections/others'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Others'
        request.meta['pageno'] = 1
        yield request
        
    
    def parsePage(self, response):
        products = response.css('div.grid-uniform.product-grid > div')        
        if len(products) == 1 and 'Sorry' in products.css('p::text').extract_first().strip():
            return
        else:
            for product in products:
                product_link = 'http://www.blissstore.in' + product.css('a::attr(href)').extract_first()
                product_name = product.css('p.product__title::text').extract_first()
                product_image = product.css('img::attr(src)').extract_first()
                product_price = product.css('p.product__price::text').extract_first().replace('Rs.','').strip()
                request = scrapy.Request(url=product_link, callback=self.parseProduct)
                request.meta['product_link'] = product_link
                request.meta['product_image'] = product_image
                request.meta['product_name'] = product_name
                request.meta['product_price'] = product_price
                request.meta['product_category'] = response.meta['category']
                yield request
            nextpage = response.meta['pageno'] + 1
            product_link = response.request.url.split('?')[0] + '?page=' + str(nextpage)            
            request = scrapy.Request(url=product_link, callback=self.parsePage)
            request.meta['category'] = response.meta['category']
            request.meta['pageno'] = nextpage
            yield request
                
    def parseProduct(self, response):
        productLink = response.meta['product_link']
        productCategory = response.meta['product_category']
        productImage = response.meta['product_image']
        productName = response.meta['product_name']
        productPrice = response.meta['product_price']
        productDesc = response.css('div.product-short-desc').extract_first()
        if productDesc:
            productDesc = strip_tags(productDesc)
        else:
            productDesc = strip_tags(response.css('div.product-single__desc.rte').extract_first())
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

        with open('HCVID322.www.blissstore.in.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
        
        HCVID322_www_blissstore_in_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
            
