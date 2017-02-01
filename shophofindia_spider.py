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
        return '|'.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class HCVID1444_shop_hofindia_com_Spider(scrapy.Spider):
    name = "HCVID1444.shop.hofindia.com"
    products_seen = []
    jsonData = []

    def closed(self, reason):
        toWrite = {'data' : HCVID1444_shop_hofindia_com_Spider.jsonData}
        with open('./json/HCVID1444.shop.hofindia.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
    
    def start_requests(self):
        page = 'http://shop.hofindia.com/premium-chairs'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Chairs|Premium'        
        yield request
        page = 'http://shop.hofindia.com/students-chairs'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Chairs|Students'        
        yield request
        page = 'http://shop.hofindia.com/professionals-chairs'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Chairs|Professionals'        
        yield request
        page = 'http://shop.hofindia.com/revolving-chairs'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Chairs|Revolving Chairs'        
        yield request
        page = 'http://shop.hofindia.com/ergonomic-chairs'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Chairs|Ergonomic Chairs'        
        yield request
        page = 'http://shop.hofindia.com/office-chairs'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Chairs|Office Chairs'        
        yield request
        page = 'http://shop.hofindia.com/leather-chairs'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Chairs|Leather Chairs'        
        yield request
        page = 'http://shop.hofindia.com/executive-chairs'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Chairs|Executive Chairs'       
        yield request
        page = 'http://shop.hofindia.com/fabric-sofa'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Sofs|Fabric Sofa'        
        yield request        
    
    def parsePage(self, response):
        products = response.css('div.category-products div.item')         
        for product in products:
            product_link = product.css('a::attr(href)').extract_first()
            product_name = product.css('p.product-name a::text').extract()
            product_name = product_name[0] + " " + product_name[1]
            product_image = product.css('img::attr(src)').extract_first()
            product_price = product.css('span.regular-price span.price::text').extract_first()
            if product_price:
                product_price = product_price.replace('₹','').strip()
            else:
                product_price = product.css('span.deals-price::text').extract_first()
                if product_price:
                    product_price = product_price.replace('₹','').strip()
                else:
                    product_price = product.css('p.minimal-price span.price::text').extract_first().replace('₹','').strip()
            request = scrapy.Request(url=product_link, callback=self.parseProduct)
            request.meta['product_link'] = product_link
            request.meta['product_image'] = product_image
            request.meta['product_name'] = product_name
            request.meta['product_price'] = product_price
            request.meta['product_category'] = response.meta['category']
            yield request
                
    def parseProduct(self, response):
        productLink = response.meta['product_link']
        productCategory = response.meta['product_category']
        productImage = response.meta['product_image']
        productName = response.meta['product_name']
        productPrice = response.meta['product_price']
        productDesc = response.css('div.std').extract_first()
        if productDesc:
            productDesc = strip_tags(productDesc)
        productSku = 'SKU-NA'

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

        with open('HCVID1444.shop.hofindia.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
        
        HCVID1444_shop_hofindia_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
            
