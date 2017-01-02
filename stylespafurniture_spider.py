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

class HCVID184_www_stylespafurniture_com_Spider(scrapy.Spider):
    name = "HCVID184.www.stylespafurniture.com"
    jsonData = []
    
    def start_requests(self):        
        link = 'http://www.stylespafurniture.com/product-range/dining/'
        request = scrapy.Request(url=link, callback = self.parseCat)
        request.meta['prod_category'] = 'Dining'
        yield request
        link = 'http://www.stylespafurniture.com/product-range/soho/'
        request = scrapy.Request(url=link, callback = self.parseCat)
        request.meta['prod_category'] = 'Soho'
        yield request
        link = 'http://www.stylespafurniture.com/product-range/living/'
        request = scrapy.Request(url=link, callback = self.parseCat)
        request.meta['prod_category'] = 'Living'
        yield request
        link = 'http://www.stylespafurniture.com/product-range/bedroom/'
        request = scrapy.Request(url=link, callback = self.parseCat)
        request.meta['prod_category'] = 'Living'
        yield request

    def parseCat(self, response):        
        items = response.css('li.product-category')
        for item in items:            
            prod_link = item.css('a::attr(href)').extract_first() + '?count=36'
            request = scrapy.Request(url=prod_link, callback = self.parse)
            request.meta['prod_category'] = response.meta['prod_category'] + '|' + item.css('h3::text').extract_first()
            yield request
                                
    def parse(self, response):
        items = response.css('li.product.type-product')
        for item in items:            
            prod_link = item.css('div.product-image a::attr(href)').extract_first()
            request = scrapy.Request(url=prod_link, callback = self.parseProduct)
            request.meta['prod_link'] = prod_link
            request.meta['prod_name'] = item.css('a.product-loop-title h3::text').extract_first()
            request.meta['prod_category'] = response.meta['prod_category']
            request.meta['prod_price'] = item.css('span.amount::text').extract_first().replace('Rs.','').strip()
            request.meta['prod_image'] = item.css('img::attr(src)').extract_first()
            yield request

    def closed(self, reason):
        toWrite = {'data' : HCVID184_www_stylespafurniture_com_Spider.jsonData}
        with open('HCVID184.www.stylespafurniture.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)            
        
    def parseProduct(self, response):
        productLink = response.meta['prod_link']
        productCategory = response.meta['prod_category']
        productName = response.meta['prod_name']
        productPrice = response.meta['prod_price']        
        productImage = response.meta['prod_image']
        productSku = response.css('span.sku::text').extract_first()

        productDesc = ''
        if response.css('div#tab-description').extract_first():
            productDesc = strip_tags(response.css('div#tab-description').extract_first())
        else:
            productDesc = 'NA'
            
        productDesc = re.sub('\n' ,'|',productDesc)
        productDesc = re.sub('\t','',productDesc)                             
        productDesc = re.sub('\r','',productDesc)
        productDesc = re.sub('[ ]+',' ',productDesc)
        productDesc = re.sub('(\| )+','|',productDesc)
        productDesc = re.sub('\|+','|',productDesc)
        productDesc = productDesc.replace('Product Description|','')
        productDesc = productDesc.strip('|')
        productDesc = productDesc.strip()        
        
        productCategory = productCategory.replace('"','``')                            
        productDesc = productDesc.replace('"','``')
        productName = productName.replace('"','``')

        productDesc = remove_non_ascii(productDesc)        
        productCategory = remove_non_ascii(productCategory)
        productName = remove_non_ascii(productName)

        with open('HCVID184.www.stylespafurniture.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
                
        HCVID184_www_stylespafurniture_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})        
