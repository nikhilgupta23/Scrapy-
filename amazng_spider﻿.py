import scrapy
import csv
import json
import re
from html.parser import HTMLParser

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else '' for i in text])

class HCVID290_www_amazng_in_Spider(scrapy.Spider):
    name = "HCVID290.www.amazng.in﻿"
    jsonData = []
    
    def start_requests(self):
        yield scrapy.Request(url='https://www.amazng.in/furniture/', callback = self.parse)        
        
    def parse(self, response):        
        items = response.css('div.col-sm-6.col-md-4.text-center')
        for item in items:            
            prod_link = 'http://amazng.in/' + str(item.css('a::attr(href)').extract_first())
            prod_name = item.css('div.fproduct-title::text').extract_first()
            prod_desc = ''
            descParts = item.css('div.hidden-data div.f-data::text').extract()
            prod_desc = 'Materials: ' + descParts[1].replace('\n','') + '|Dimensions: ' +descParts[3]
            
            request = scrapy.Request(url=prod_link, callback = self.parseProduct)
            request.meta['prod_link'] = prod_link                
            request.meta['prod_name'] = prod_name
            request.meta['prod_desc'] = prod_desc            
            yield request

    def closed(self, reason):
        toWrite = {'data' : HCVID290_www_amazng_in_Spider.jsonData}
        with open('HCVID290.www.amazng.in﻿.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
        
    def parseProduct(self, response):        
        productLink = response.meta['prod_link']
        productName = response.meta['prod_name']
        productDesc = response.meta['prod_desc']

        productPrice = response.css('div.pricebox span::text').extract_first()
        productImage = response.css('div.imageDiv img::attr(src)').extract_first()        
        productSku = 'SKU-NA'
        productCategory = response.css('div.collection_pro_name::text').extract_first().strip()
        
        productDesc = str(response.css('div.shrotdesc p::text').extract_first()) + '|' + productDesc        

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
                
        with open('HCVID290.www.amazng.in.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
        
        HCVID290_www_amazng_in_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
