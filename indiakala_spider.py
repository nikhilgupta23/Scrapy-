import scrapy
import csv
import json
import re
from html.parser import HTMLParser

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else '' for i in text])

class HCVID174_www_indiakala_com_Spider(scrapy.Spider):
    name = "HCVID174.www.indiakala.com"
    jsonData = []
    
    def start_requests(self):
        for x in range(1,33):
            link = 'http://indiakala.com/home-living.html?p='+str(x)
            yield scrapy.Request(url=link, callback = self.parse)        
        
    def parse(self, response):        
        items = response.css('div.product-item')    
        for item in items:            
            prod_link = item.css('div.imageHolder a::attr(href)').extract_first()
            prod_name = item.css('div.img-des::text').extract_first().strip()
            prod_price = item.css('span.price-container span.price::text').extract_first().replace('₹','').strip()
            prod_image = item.css('div.imageHolder img::attr(src)').extract_first()
            request = scrapy.Request(url=prod_link, callback = self.parseProduct)
            request.meta['prod_link'] = prod_link  
            request.meta['prod_name'] = prod_name
            request.meta['prod_price'] = prod_price
            request.meta['prod_image'] = prod_image
            yield request

    def closed(self, reason):
        toWrite = {'data' : HCVID174_www_indiakala_com_Spider.jsonData}
        with open('HCVID174.www.indiakala.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
        
    def parseProduct(self, response):        
        productLink = response.meta['prod_link']
        productName = response.meta['prod_name']
        productPrice = response.meta['prod_price']
        productImage = response.meta['prod_image']
        productSku = response.css('div.stock-area p:last-child::text').extract_first().replace('Product Code :','').strip()
        productCategory = 'Home & Living'        
        productDesc = response.css('p.p-des::text').extract_first()
        
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
                
        with open('HCVID174.www.indiakala.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
        
        HCVID174_www_indiakala_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
