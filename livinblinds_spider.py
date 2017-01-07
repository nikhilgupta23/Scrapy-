import scrapy
import csv
import json
import re
from html.parser import HTMLParser

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else '' for i in text])

class HCVID404_livinblinds_com_Spider(scrapy.Spider):
    name = "HCVID404.livinblinds.com"
    jsonData = []
    
    def start_requests(self):        
        link = 'http://livinblinds.com/category/wooden-window-blinds'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Wooden'
        yield request
        link = 'http://livinblinds.com/category/collinear-window-blinds'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Collinear'
        yield request
        link = 'http://livinblinds.com/category/cellular-window-blinds'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Cellular'
        yield request
        link = 'http://livinblinds.com/category/roman-window-blinds'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Roman'
        yield request
        link = 'http://livinblinds.com/category/roller-window-blinds'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Roller'
        yield request
        link = 'http://livinblinds.com/category/zebra-window-blinds'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Zebra'
        yield request
        link = 'http://livinblinds.com/category/open-roman-window-blinds'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Open Roman'
        yield request
        link = 'http://livinblinds.com/category/apex-window-blinds'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Apex'
        yield request
        link = 'http://livinblinds.com/category/panel-window-blinds'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Panel'
        yield request
                                
    def parse(self, response):
        links = response.css('div.block-matrix')
        for link in links:            
            page = 'http://livinblinds.com/' + link.css('a::attr(href)').extract_first()
            request = scrapy.Request(url=page, callback = self.parsePage)            
            request.meta['prod_category'] = response.meta['prod_category'] + '|' + link.css('h3::text').extract_first()
            yield request

    def parsePage(self, response):
        items = response.css('div#tabs li')
        for item in items:            
            prod_link = 'http://livinblinds.com/' + item.css('a.btn-shop::attr(href)').extract_first()
            prod_name = item.css('h3::text').extract_first()
            request = scrapy.Request(url=prod_link, callback = self.parseProduct)
            request.meta['prod_link'] = prod_link
            request.meta['prod_name'] = prod_name
            request.meta['prod_category'] = response.meta['prod_category']
            yield request

    def closed(self, reason):
        toWrite = {'data' : HCVID404_livinblinds_com_Spider.jsonData}
        with open('HCVID404.livinblinds.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)            
        
    def parseProduct(self, response):
        productLink = response.meta['prod_link']
        productCategory = response.meta['prod_category']
        productName = response.meta['prod_name']
        productImage = 'http://livinblinds.com/' +  response.css('div.outer-container-shadow img::attr(src)').extract_first()
        productDesc = 'NA'
        productPrice = response.css('input#price::attr(value)').extract_first()
        productSku ='SKU-NA'
                            
        productCategory = productCategory.replace('"','``')                            
        productName = productName.replace('"','``')

        productCategory = remove_non_ascii(productCategory)
        productName = remove_non_ascii(productName)

        with open('HCVID404.livinblinds.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})

        HCVID404_livinblinds_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
