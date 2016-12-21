import scrapy
import csv
import json
import re
from html.parser import HTMLParser

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else '' for i in text])

class HCVID394_claymango_com_Spider(scrapy.Spider):
    name = "HCVID394.claymango.com"
    jsonData = []
    
    def start_requests(self):            
        link = 'http://claymango.com/categorypage.php?maincat=HOME+%2B+LIVING'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'HOME + LIVING'
        yield request
        link = 'http://claymango.com/categorypage.php?maincat=TECH'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'TECH'
        yield request
        link = 'http://claymango.com/categorypage.php?maincat=VINTAGE'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'VINTAGE'
        yield request
        link = 'http://claymango.com/categorypage.php?maincat=HAND+MADE'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'HAND MADE'        
        yield request
                    
    def parse(self, response):        
        items = response.css('div.pricing-tables div.column')    
        for item in items:
            prod_link = 'http://claymango.com/' + item.css('ul.features li a::attr(href)').extract_first()
            prod_price = item.css('ul.features div.productdescriptionbox div div::text').extract_first().replace('Rs','').strip()
            
            request = scrapy.Request(url=prod_link, callback = self.parseProduct)
            request.meta['prod_link'] = prod_link                
            request.meta['prod_price'] = prod_price
            request.meta['prod_category'] = response.meta['prod_category']
            yield request

    def closed(self, reason):
        toWrite = {'data' : HCVID394_claymango_com_Spider.jsonData}
        with open('HCVID394.claymango.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
        
    def parseProduct(self, response):        
        productLink = response.meta['prod_link']
        productPrice = response.meta['prod_price']
        productName = response.css('div.rightsidediv p strong::text').extract_first()
        productMerchant = response.css('div.rightsidediv p a::text').extract_first()
        productImage = 'http://claymango.com/' + response.css('img.mainprodimage::attr(src)').extract_first()
        productCategory = response.meta['prod_category'] if response.meta['prod_category'] else '' + '|' + response.css('div.product_cat_header a:last-child::text').extract_first()
        productSku = 'SKU-NA'
        productDesc = ''
        productDescParts = response.css('div#featurediv::text').extract()
        for part in productDescParts:
            productDesc += part + '|'
        productDescParts = response.css('div#descriptiondiv::text').extract()
        for part in productDescParts:
            productDesc += part + '|'

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

        with open('HCVID394.claymango.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"'+str(productMerchant)+'"'})
                        
        HCVID394_claymango_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': productMerchant})
