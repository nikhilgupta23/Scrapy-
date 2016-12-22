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

class HCVID215_www_neerja_com_Spider(scrapy.Spider):
    name = "HCVID215.www.neerja.com"
    jsonData = []
    
    def start_requests(self):            
        link = 'https://www.neerja.com/catalog'
        request = scrapy.Request(url=link, callback = self.parseCategories)        
        yield request

    def parseCategories(self, response):
        cats = response.css('table.category tbody td.category')        
        for cat in cats:
            link = ''
            try:
                link = 'https://www.neerja.com' + cat.css('div a::attr(href)').extract_first()
            except:
                return
            subavailable = ['https://www.neerja.com/category/decorative-plates', 'https://www.neerja.com/category/tiles', 'https://www.neerja.com/category/alphabet-tiles', 'https://www.neerja.com/category/jewellery', 'https://www.neerja.com/category/cabinet-knobs', 'https://www.neerja.com/category/bowls', 'https://www.neerja.com/category/festival-special']
            request = None
            if link in subavailable:
                request = scrapy.Request(url=link, callback = self.parseCategories)
            else:                
                request = scrapy.Request(url=link, callback = self.parse)
            prod_category = ''
            if 'prod_category' in response.meta:
                prod_category = response.meta['prod_category'] + '|'
            prod_category += cat.css('strong a::text').extract_first()            
            request.meta['prod_category'] = prod_category
            yield request
                    
    def parse(self, response):        
        items = response.css('table.colu td')        
        for item in items:
            prod_link = 'https://www.neerja.com' + item.css('span.catalog-grid-title a::attr(href)').extract_first()
            prod_price = item.css('span.uc-price::text').extract_first().replace('Rs','').strip()
            prod_name = item.css('span.catalog-grid-title a::text').extract_first()
            prod_sku = item.css('span.catalog-grid-ref::text').extract_first().strip()
            request = scrapy.Request(url=prod_link, callback = self.parseProduct)
            request.meta['prod_link'] = prod_link                
            request.meta['prod_price'] = prod_price            
            request.meta['prod_sku'] = prod_sku
            request.meta['prod_name'] = prod_name
            request.meta['prod_category'] = response.meta['prod_category']
            yield request

    def closed(self, reason):
        toWrite = {'data' : HCVID215_www_neerja_com_Spider.jsonData}
        with open('HCVID215.www.neerja.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
        
    def parseProduct(self, response):
        productLink = response.meta['prod_link']
        productPrice = response.meta['prod_price']
        productName = response.meta['prod_name']
        productSku = response.meta['prod_sku']
        productCategory = response.meta['prod_category']
        productMerchant = 'NA'
        productImage = response.css('div.main-product-image img::attr(src)').extract_first()
        
        productDescParts = response.css('div.product-body p').extract()
        if not productDescParts:
            productDescParts = response.css('div.product-body div').extract()
        productDesc = ''
        for part in productDescParts:
            productDesc += strip_tags(part) + '|'
        productDesc = productDesc.strip('|')
            
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

        with open('HCVID215.www.neerja.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
        
        HCVID215_www_neerja_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': productMerchant})
