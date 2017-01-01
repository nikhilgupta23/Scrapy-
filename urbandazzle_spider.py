import scrapy
import csv
import json
import re
from html.parser import HTMLParser

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else '' for i in text])

class HCVID275_www_urbandazzle_com_Spider(scrapy.Spider):
    name = "HCVID275.www.urbandazzle.com"
    jsonData = []
    
    def start_requests(self):
        for x in range(1,87):
            link = 'https://www.urbandazzle.com/catalog/category/data/id/236?p='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            yield request
        for x in range(1,70):
            link = 'https://www.urbandazzle.com/catalog/category/data/id/238?p='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            yield request
        for x in range(1,41):
            link = 'https://www.urbandazzle.com/catalog/category/data/id/242?p='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            yield request
        for x in range(1,10):
            link = 'https://www.urbandazzle.com/catalog/category/data/id/147?p='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            yield request
        for x in range(1,24):
            link = 'https://www.urbandazzle.com/catalog/category/data/id/249?p='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            yield request
                                
    def parse(self, response):        
        items = response.css('div.product-list-view.product-margin')
        for item in items:
            prod_link = item.css('div.product-image-list a::attr(href)').extract_first()
            prod_price = item.css('div.price::text').extract_first()
            if not prod_price:
                prod_price = item.css('p.old-price span.price::text').extract_first().replace('Rs.','').strip()
            else:
                prod_price = prod_price.replace('Rs.','').strip()
            prod_name = item.css('span.product-detail::text').extract_first()
            request = scrapy.Request(url=prod_link, callback = self.parseProduct)
            request.meta['prod_link'] = prod_link
            request.meta['prod_name'] = prod_name           
            request.meta['prod_price'] = prod_price            
            yield request

    def closed(self, reason):
        toWrite = {'data' : HCVID275_www_urbandazzle_com_Spider.jsonData}
        with open('HCVID275.www.urbandazzle.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
        
    def parseProduct(self, response):        
        productLink = response.meta['prod_link']        
        productPrice = response.meta['prod_price']
        productName = response.meta['prod_name']
        productImage = response.css('img.ms-big-image::attr(src)').extract_first()
        productSku = response.css('span.raa_sku::text').extract_first()

        productCategories = response.css('ul.breadcrumb-listpage li a::text').extract()        
        productCategory = ''
        for catnum in range(1,len(productCategories)):
            productCategory += productCategories[catnum] + '|'
        productCategory = productCategory.strip('|')

        productDesc = response.css('meta[name="description"]::attr(content)').extract_first().strip(': Urbandazzle')
        productMerchant = response.xpath('//div[@itemprop="brand"]/a/text()').extract_first().strip()
        
        productCategory = productCategory.replace('"','``')
        productDesc = productDesc.strip('|')
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

        with open('HCVID275.www.urbandazzle.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"'+str(productMerchant)+'"'})

        HCVID275_www_urbandazzle_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': productMerchant})
        
