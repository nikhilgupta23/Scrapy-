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

class HCVID237_www_addresshome_com_Spider(scrapy.Spider):
    name = "HCVID237.www.addresshome.com"
    jsonData = []
    
    def start_requests(self):
        for x in range(1,3):
            link = 'http://www.addresshome.com/bed-linen?p='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Bed Linen'
            yield request
        for x in range(1,3):
            link = 'http://www.addresshome.com/tableware?p='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Tableware'
            yield request
        for x in range(1,4):
            link = 'http://www.addresshome.com/home-decor?p='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Home Decor'
            yield request
        for x in range(1,4):
            link = 'http://www.addresshome.com/gifts?p='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Gifts'
            yield request
        for x in range(1,3):
            link = 'http://www.addresshome.com/new-arrivals?p='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'New Arrivals'
            yield request
        link = 'http://www.addresshome.com/candlewares?p=1'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Candlewares'
        yield request
        
    def parse(self, response):        
        items = response.css('li.item.last')    
        for item in items:            
            prod_link = item.css('a::attr(href)').extract_first()
            prod_name = item.css('h2.product-name a::text').extract_first()
            prod_image = item.css('img::attr(src)').extract_first()
            prod_price = str(item.css('span.regular-price span.price::text').extract_first()).replace('Rs.','').strip()
            
            request = scrapy.Request(url=prod_link, callback = self.parseProduct)
            request.meta['prod_link'] = prod_link              
            request.meta['prod_name'] = prod_name
            request.meta['prod_price'] = prod_price
            request.meta['prod_image'] = prod_image
            request.meta['prod_category'] = response.meta['prod_category']
            yield request

    def closed(self, reason):
        toWrite = {'data' : HCVID237_www_addresshome_com_Spider.jsonData}
        with open('HCVID237.www.addresshome.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
        
    def parseProduct(self, response):        
        productLink = response.meta['prod_link']
        productName = response.meta['prod_name']
        productPrice = response.meta['prod_price']
        productImage = response.meta['prod_image']
        productCategory = response.meta['prod_category']
        
        productSku = str(response.css('div.product-shop p::text').extract_first()).replace('SKU :','').strip()

        productDesc = ''
        descParts = response.css('div.std[itemprop=description]::text').extract()        
        for part in descParts:
            productDesc += part.strip() + '|'
        detailParts = response.css('table.data-table tr td::text').extract()        
        productDesc += 'SHORTNAME:' + detailParts[0]
        productDesc += '|SIZE:' + detailParts[1]
        productDesc += '|MATERIAL:' + detailParts[2]
        productDesc += '|COLOR:' + detailParts[3]
        
        productCategory = productCategory.replace('"','``')        
        productDesc = re.sub('\n' ,'|',productDesc)
        productDesc = re.sub('\t','',productDesc)                             
        productDesc = re.sub('\r','',productDesc)
        productDesc = re.sub('[ ]+',' ',productDesc)
        productDesc = re.sub('(\| )+','|',productDesc)
        productDesc = re.sub('\|+','|',productDesc)
        productDesc = productDesc.replace('"','``')
        productName = productName.replace('"','``')
        
        productDesc = remove_non_ascii(productDesc)        
        productCategory = remove_non_ascii(productCategory)
        productName = remove_non_ascii(productName)
                
        with open('HCVID237.www.addresshome.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
        
        HCVID237_www_addresshome_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
