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

class HCVID186_www_curtisandhayes_com_Spider(scrapy.Spider):
    name = "HCVID186.www.curtisandhayes.com"
    jsonData = []
    
    def start_requests(self):
        for x in range(1,4):
            link = 'https://www.curtisandhayes.com/chairs.html?limit=36&p='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Chairs'
            yield request
        for x in range(1,3):
            link = 'https://www.curtisandhayes.com/sofas.html?limit=36&p='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Sofas'
            yield request
        for x in range(1,4):
            link = 'https://www.curtisandhayes.com/tables.html?limit=36&p='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Tables'
            yield request
        for x in range(1,3):
            link = 'https://www.curtisandhayes.com/storage.html?limit=36&p='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Storage'
            yield request
        for x in range(1,3):
            link = 'https://www.curtisandhayes.com/lighting.html?limit=36&p='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Lightning'
            yield request
        for x in range(1,3):
            link = 'https://www.curtisandhayes.com/home-decor.html?limit=36&p='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Home Decor'
            yield request
        for x in range(1,8):
            link = 'https://www.curtisandhayes.com/home-furnishings.html?limit=36&p='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Home Furnishings'
            yield request
        link = 'https://www.curtisandhayes.com/bedroom.html?limit=36'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Bedroom'
        yield request
        link = 'https://www.curtisandhayes.com/wardrobes.html?limit=36'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Wardrobes'
        yield request
                    
    def parse(self, response):        
        items = response.css('div.item')    
        for item in items:
            prod_link = item.css('h3.product-name a::attr(href)').extract_first()
            prod_name = item.css('h3.product-name a::text').extract_first()
            request = scrapy.Request(url=prod_link, callback = self.parseProduct)
            request.meta['prod_link'] = prod_link                
            request.meta['prod_name'] = prod_name
            request.meta['prod_category'] = response.meta['prod_category']
            yield request

    def closed(self, reason):
        toWrite = {'data' : HCVID186_www_curtisandhayes_com_Spider.jsonData}
        with open('HCVID186.www.curtisandhayes.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
        
    def parseProduct(self, response):        
        productLink = response.meta['prod_link']
        productName = response.meta['prod_name']
        productPrice = response.css('span.regular-price span.price::text').extract_first().replace('Rs.','').strip()
        productImage = response.css('img[itemprop=image]::attr(data-src)').extract_first()
        productCategory = response.meta['prod_category']
        productDesc = ''
        try:
            productDesc = response.css('div[itemprop=description]::text').extract_first() + '|'
        except TypeError:
            pass
        descParts = response.css('div.hor_1 div div.std').extract_first()
        productDesc += re.sub('<[^>]*>', '', descParts)        
        
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
                
        with open('HCVID186.www.curtisandhayes.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
        
        HCVID186_www_curtisandhayes_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
