import scrapy
import csv
import json
import re
from html.parser import HTMLParser
from selenium import webdriver

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

class HCVID273_hangit_co_in_Spider(scrapy.Spider):
    name = "HCVID273.hangit.co.in"    
    jsonData = []
    products_seen = []
    
    def closed(self, reason):
        toWrite = {'data' : HCVID273_hangit_co_in_Spider.jsonData}
        with open('HCVID273.hangit.co.in.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
    
    def start_requests(self):
        url = "http://hangit.co.in/"
        yield scrapy.Request(url=url, callback=self.parse)
        
    def parse(self, response):
        x = response.css('div#menu ul > li')
        for columns in x:
            name = columns.css('a::text').extract_first()            
            prod_cat_head = name + '|'            
            cats = columns.css('ul li')        
            for cat in cats:
                page = cat.css('a::attr(href)').extract_first()
                prod_cat = prod_cat_head + cat.css('a::text').extract_first()
                request = scrapy.Request(url=page, callback = self.parsePage)
                request.meta['prod_category'] = prod_cat
                request.meta['pageno'] = 1
                yield request
                        
    def parsePage(self, response):
        products = response.css('div.product-list > div')
        if not products:
            return
        for product in products:
            product_link = product.css('div.image a::attr(href)').extract_first()
            product_image = product.css('div.image img::attr(src)').extract_first()
            product_name = product.css('div.name a::text').extract_first()
            product_price = product.css('span.price-old::text').extract_first().replace('Rs.','').strip()
            request = scrapy.Request(url=product_link, callback=self.parseProduct)
            request.meta['prod_link'] = product_link
            request.meta['prod_name'] = product_name
            request.meta['prod_price'] = product_price
            request.meta['prod_image'] = product_image
            request.meta['prod_category'] = response.meta['prod_category']      
            yield request
            
            page = response.meta['pageno'] + 1
            nextpage = response.request.url.split('?')[0] + '?page=' + str(page)
            request = scrapy.Request(url=nextpage, callback = self.parsePage)
            request.meta['prod_category'] = response.meta['prod_category']
            request.meta['pageno'] = page
            yield request        
                
    def parseProduct(self, response):
        productLink = response.meta['prod_link']
        productImage = response.meta['prod_image']
        productCategory = response.meta['prod_category']
        productName = response.meta['prod_name']
        productDesc = strip_tags(response.css('div#tab-description p').extract_first())
        productPrice = response.meta['prod_price']
        productSku = 'SKU-NA'
        
        productDesc = re.sub('\n' ,'|',productDesc)
        productDesc = re.sub('\t','',productDesc)                             
        productDesc = re.sub('\r','',productDesc)
        productDesc = re.sub('[ ]+',' ',productDesc)
        productDesc = re.sub('(\| )+','|',productDesc)
        productDesc = re.sub('\|+','|',productDesc)
        productDesc = productDesc.strip('|')
        productDesc = productDesc.replace('"','``')
        productName = productName.replace('"','``')
        productCategory = productCategory.replace('"','``')        

        productDesc = remove_non_ascii(productDesc)        
        productCategory = remove_non_ascii(productCategory)
        productName = remove_non_ascii(productName)

        with open('HCVID273.hangit.co.in.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})

        HCVID273_hangit_co_in_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
            
