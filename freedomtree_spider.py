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
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class HCVID39_freedomtree_in_Spider(scrapy.Spider):
    name = "HCVID39.freedomtree.in"
    jsonData = []
    
    def start_requests(self):
        for x in range(1,3):
            link = 'https://freedomtree.in/collections/fabrics?page='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Curtains & Upholstery'
            yield request
        for x in range(1,3):
            link = 'https://freedomtree.in/collections/bedroom?page='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Bed & Bath'
            yield request
        for x in range(1,3):
            link = 'https://freedomtree.in/collections/cushions?page='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Cushions'
            yield request
        for x in range(1,6):
            link = 'https://freedomtree.in/collections/dining?page='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Dining & Entertaining'
            yield request
        for x in range(1,4):
            link = 'https://freedomtree.in/collections/cushions-and-decor?page='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Decor'
            yield request
        link = 'https://freedomtree.in/collections/kids'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Kids'
        yield request
        link = 'https://freedomtree.in/collections/furniture'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Furniture'
        yield request
        link = 'https://freedomtree.in/collections/lamps'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Lamps'
        yield request
        link = 'https://freedomtree.in/collections/rugs'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Rugs'
        yield request
        
                    
    def parse(self, response):        
        items = response.css('div.four.columns.thumbnail')    
        for item in items:
            prod_link = 'https://freedomtree.in' + item.css('a::attr(href)').extract_first()
            request = scrapy.Request(url=prod_link, callback = self.parseProduct)
            request.meta['prod_link'] = prod_link
            request.meta['prod_category'] = response.meta['prod_category']
            yield request

    def closed(self, reason):
        toWrite = {'data' : HCVID39_freedomtree_in_Spider.jsonData}
        with open('HCVID39.freedomtree.in.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
        
    def parseProduct(self, response):        
        productLink = response.meta['prod_link']
        productImage = response.css('ul.slides li a::attr(href)').extract_first()
        productCategories = response.css('div.meta p span a::text').extract()        
        productCategory = ''
        for category in productCategories:
            productCategory += category + ','
        productCategory = productCategory.strip('|')
        productDesc = ''                
        descParts = response.css('div.description ul li').extract()
        for part in descParts:
            productDesc += strip_tags(part) + '|'
            
        scripts = response.css('script[type=text\/javascript]').extract()
        for script in scripts:
            if 'var meta' in script:
                data = json.loads(re.search('var meta = (.*?);', script).group(1))
                productMerchant = data["product"]["vendor"]
                variants = data["product"]["variants"]
                for variant in variants:
                    productSku = variant["sku"]
                    productPrice = variant["price"]
                    productName = variant["name"]

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

                    with open('HCVID39.freedomtree.in.csv', 'a', newline='') as csvfile:
                        fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
                        writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"'+str(productMerchant)+'"'})        
                            
                    HCVID39_freedomtree_in_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
                break
        
