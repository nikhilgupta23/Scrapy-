import scrapy
import csv
import json
import re

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else '' for i in text])

class HCVID207_nomad_in_Spider(scrapy.Spider):
    name = "HCVID207.no-mad.in"
    jsonData = []

    def start_requests(self):
        for x in range(1,10):
            link = 'https://www.no-mad.in/product-category/home-textiles/page/'+str(x)+'/?v=c86ee0d9d7ed'
            yield scrapy.Request(url=link, callback = self.parse)
        for x in range(1,4):
            link = 'https://www.no-mad.in/product-category/table/page/'+str(x)+'/?v=c86ee0d9d7ed'
            yield scrapy.Request(url=link, callback = self.parse)
        for x in range(1,5):
            link = 'https://www.no-mad.in/product-category/fabrics/page/'+str(x)+'/?v=c86ee0d9d7ed'
            yield scrapy.Request(url=link, callback = self.parse)
        for x in range(1,3):
            link = 'https://www.no-mad.in/product-category/furniture-2/page/'+str(x)+'/?v=c86ee0d9d7ed'
            yield scrapy.Request(url=link, callback = self.parse)
        for x in range(1,6):
            link = 'https://www.no-mad.in/product-category/accessories/page/'+str(x)+'/?v=c86ee0d9d7ed'
            yield scrapy.Request(url=link, callback = self.parse)                        
            
    def parse(self, response):        
        source = response.request.url
        items = response.css('div.product-container')
        for item in items:            
            prod_link = item.css('figure a::attr(href)').extract_first()
            request = None
            if '?v=' in prod_link:
                request = scrapy.Request(url=prod_link, callback = self.parseProduct)
            else:
                request = scrapy.Request(url=prod_link+'?v=c86ee0d9d7ed', callback = self.parseProduct)
            request.meta['prod_link'] = prod_link                 
            yield request

    def closed(self, reason):
        toWrite = {'data' : HCVID207_nomad_in_Spider.jsonData}
        with open('HCVID207.no-mad.in.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, indent=4)

    @staticmethod
    def saveProduct(productName, productDesc, productImage, productPrice, productSku, productCategory, productLink):
        if not productSku:
            productSku = 'SKU-NA'
        productCategory = productCategory.replace('"','``')
        productDesc = productDesc.strip()
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
        
        with open('HCVID207.no-mad.in.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})

        HCVID207_nomad_in_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
        
    def parseProduct(self, response):
        productLink = response.meta['prod_link']
        productCategories = response.css('div.product_meta span.posted_in a[rel="tag"]::text').extract()
        productCategory = ''
        for category in productCategories:
            productCategory += category + ','
        productCategory = productCategory[:-1]
        parts = response.css('div.tab-content p::text').extract()
        productDesc = ''
        for part in parts:
            productDesc += part + '|'
        
        productName = response.css('h1::text').extract_first()        
        productImage = response.css('img.attachment-shop_single::attr(src)').extract_first()
        productSku = response.css('span.sku::text').extract_first()
        
        productPrice = response.css('div.summary span.amount::text').extract_first()
        if not productPrice:
            jsonData = response.css('form.variations_form.cart::attr(data-product_variations)').extract_first()
            jsonData = jsonData.replace('&quot;','"')
            jsonData = json.loads(jsonData)
            for variant in jsonData:
                productImage = variant["image_link"]
                productSku = variant["sku"]
                productPrice = variant["display_regular_price"]
                HCVID207_nomad_in_Spider.saveProduct(productName, productDesc, productImage, productPrice, productSku, productCategory, productLink)
        else:
            productPrice = productPrice.replace('Rs.','').replace('.00','').replace(',','').strip()
            HCVID207_nomad_in_Spider.saveProduct(productName, productDesc, productImage, productPrice, productSku, productCategory, productLink)

        
