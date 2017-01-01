import scrapy
import csv
import json
import re
from html.parser import HTMLParser

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else '' for i in text])

class HCVID258_www_91degree_com_Spider(scrapy.Spider):
    name = "HCVID258.www.91degree.com"
    jsonData = []
    
    def start_requests(self):
        for x in range(1,3):
            link = 'http://91degree.com/table-decor.html?p='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Table Decor'
            yield request
        for x in range(1,5):
            link = 'http://91degree.com/votives.html?p='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Decor'
            yield request
        link = 'http://91degree.com/lights.html'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Lights'
        yield request
        link = 'http://91degree.com/wall-decor.html'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Wall Decor'
        yield request
        link = 'http://91degree.com/bowls.html'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Bowls'
        yield request
                                
    def parse(self, response):        
        items = response.css('div.product_detail_page div.item-inner')
        for item in items:            
            prod_link = item.css('a.product_link::attr(href)').extract_first()
            request = scrapy.Request(url=prod_link, callback = self.parseVariants)
            request.meta['prod_category'] = response.meta['prod_category']
            yield request

    def closed(self, reason):
        toWrite = {'data' : HCVID258_www_91degree_com_Spider.jsonData}
        with open('HCVID258.www.91degree.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
            
    def parseVariants(self, response):
        
        variants = response.css('div.color-options div.color_option')
        if variants:
            for variant in variants:
                prod_link = variant.css('a::attr(data-url)').extract_first()
                request = scrapy.Request(url=prod_link, callback = self.parseProduct, dont_filter=True)
                request.meta['prod_link'] = prod_link
                request.meta['prod_category'] = response.meta['prod_category']
                yield request
        else:
            prod_link = response.request.url
            request = scrapy.Request(url=prod_link, callback = self.parseProduct, dont_filter=True)
            request.meta['prod_link'] = prod_link
            request.meta['prod_category'] = response.meta['prod_category']
            yield request
        
    def parseProduct(self, response):
        productLink = response.meta['prod_link']
        productCategory = response.meta['prod_category']
        productName = response.css('div.product-name h1::text').extract_first()
        productPrice = response.css('span.regular-price span.price::text').extract_first().replace('₹','').strip()
        productImage = response.css('div.product-image-box img::attr(src)').extract_first()
        productSku = response.css('div.accordion_in div.attr-content-box span.attr-content::text').extract_first()
        productDesc = response.css('div.accordion_in:nth-child(2) span.attr-content::text').extract_first()

        productDesc = re.sub('\n' ,'|',productDesc)
        productDesc = re.sub('\t','',productDesc)                             
        productDesc = re.sub('\r','',productDesc)
        productDesc = re.sub('[ ]+',' ',productDesc)
        productDesc = re.sub('(\| )+','|',productDesc)
        productDesc = re.sub('\|+','|',productDesc)        
        productDesc = productDesc.strip('|')
        productDesc = productDesc.strip()        
        
        productCategory = productCategory.replace('"','``')                            
        productDesc = productDesc.replace('"','``')
        productName = productName.replace('"','``')

        productDesc = remove_non_ascii(productDesc)        
        productCategory = remove_non_ascii(productCategory)
        productName = remove_non_ascii(productName)
        
        with open('HCVID258.www.91degree.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
            
        HCVID258_www_91degree_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})        
