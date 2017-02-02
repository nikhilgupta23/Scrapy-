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

class HCVID308_www_scarletsplendour_com_Spider(scrapy.Spider):
    name = "HCVID308.www.scarletsplendour.com"
    jsonData = []

    def closed(self, reason):
        toWrite = {'data' : HCVID308_www_scarletsplendour_com_Spider.jsonData}
        with open('./json/HCVID308.www.scarletsplendour.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
    
    def start_requests(self):
        page = 'http://www.scarletsplendour.com/vanilla-noir/'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Vanilla Noir'        
        yield request
        page = 'http://www.scarletsplendour.com/fools-gold/'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Fool\'s Gold'        
        yield request
        page = 'http://www.scarletsplendour.com/karesansui/'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Karesnsui'        
        yield request
        page = 'http://www.scarletsplendour.com/gufram/'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Gufram'        
        yield request
        page = 'http://www.scarletsplendour.com/mandala/'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Mandala'        
        yield request
        page = 'http://www.scarletsplendour.com/luce-naga/'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Lucenaga'        
        yield request
        page = 'http://www.scarletsplendour.com/dark-angel/'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Dark Angel'        
        yield request
        page = 'http://www.scarletsplendour.com/flora/'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Flora'
        yield request
        page = 'http://www.scarletsplendour.com/mira/'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Mira'        
        yield request
        page = 'http://www.scarletsplendour.com/terra/'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Terra'        
        yield request
        page = 'http://www.scarletsplendour.com/scarlet-eclectics/'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Scarlet Eclectics'        
        yield request
    
    def parsePage(self, response):
        products = response.css('ul.products.collection.grid > li')         
        for product in products:
            product_link = product.css('a::attr(href)').extract_first()
            product_name = strip_tags(product.css('div.title').extract_first())
            product_image = product.css('img::attr(src)').extract_first()
            request = scrapy.Request(url=product_link, callback=self.parseProduct)
            request.meta['product_link'] = product_link
            request.meta['product_image'] = product_image
            request.meta['product_name'] = product_name
            request.meta['product_category'] = response.meta['category']
            yield request
                
    def parseProduct(self, response):
        productLink = response.meta['product_link']
        productCategory = response.meta['product_category']
        productImage = response.meta['product_image']
        productName = response.meta['product_name']
        productPrice = 'NA'
        productDesc = response.css('meta[name="description"]::attr(content)').extract_first()
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

        productName = productName.replace('|','')
        
        productDesc = remove_non_ascii(productDesc)        
        productCategory = remove_non_ascii(productCategory)
        productName = remove_non_ascii(productName)

        with open('HCVID308.www.scarletsplendour.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})

        HCVID308_www_scarletsplendour_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
            
