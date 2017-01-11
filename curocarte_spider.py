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

class HCVID409_www_curocarte_com_Spider(scrapy.Spider):
    name = "HCVID409.www.curocarte.com"
    jsonData = []
    products_seen = []
    
    def closed(self, reason):
        toWrite = {'data' : HCVID409_www_curocarte_com_Spider.jsonData}
        with open('./json/HCVID409.www.curocarte.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
    
    def start_requests(self):
        url = "https://www.curocarte.com/in/"
        yield scrapy.Request(url=url, callback=self.parse)
        
    def parse(self, response):
        x = response.css('ul.nav li#62 ul.level0 li.level1')
        print(x)
        for columns in x:
            name = columns.css('a span::text').extract_first()
            prod_cat_head = name + '|'
            cats = columns.css('ul.level1 li.level2')
            for cat in cats:
                page = cat.css('a::attr(href)').extract_first() + '&limit=180'
                prod_cat = prod_cat_head + cat.css('a span::text').extract_first()
                request = scrapy.Request(url=page, callback = self.parsePage)
                request.meta['prod_category'] = prod_cat
                yield request
                        
    def parsePage(self, response):        
        products = response.css('ul.products-grid > li')
        for product in products:            
            product_link = product.css('div.product-img a::attr(href)').extract_first()
            product_image = product.css('div.product-img a img::attr(src)').extract_first()
            request = scrapy.Request(url=product_link, callback=self.parseProduct)
            request.meta['prod_link'] = product_link
            request.meta['prod_image'] = product_image
            request.meta['prod_category'] = response.meta['prod_category']      
            yield request
                
    def parseProduct(self, response):
        productLink = response.meta['prod_link']
        productImage = response.meta['prod_image']
        productCategory = response.meta['prod_category']
        productName = response.css('span.h1::text').extract_first()
        productDesc = response.css('div#tabs-1').extract_first()
        if not productDesc:
            productDesc = 'NA'
        else:
            productDesc = strip_tags(productDesc)
        productPrice = response.css('span.regular-price span.price::text').extract_first().replace('₹','').strip()
        productSku = response.css('div.product-sku-no::text').extract_first()

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

        with open('HCVID409.www.curocarte.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
        
        HCVID409_www_curocarte_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
            
