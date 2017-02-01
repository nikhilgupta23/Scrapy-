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

class HCVID312_mezzohome_com_Spider(scrapy.Spider):
    name = "HCVID312.mezzohome.com"
    products_seen = []
    jsonData = []

    def closed(self, reason):
        toWrite = {'data' : HCVID312_mezzohome_com_Spider.jsonData}
        with open('./json/HCVID312.mezzohome.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
    
    def start_requests(self):
        url = "http://mezzohome.com/index.php"
        yield scrapy.Request(url=url, callback=self.parse)
        
    def parse(self, response):        
        x = response.css('ul.nav li.test')        
        for columns in x:
            head_category = columns.css('a::text').extract_first().strip()
            if head_category != 'FASHION' and head_category != 'SHOP BY COLLECTION':
                list_items = columns.css('ul > li')
                for item in list_items:
                    page = 'http://mezzohome.com/' + item.css('a::attr(href)').extract_first()
                    sub_category = item.css('a::text').extract_first().strip()
                    if page is not None:                    
                        request = scrapy.Request(url= page, callback = self.parsePage)                    
                        request.meta['category'] = str(head_category) + '|' + str(sub_category)
                        yield request        

    def parsePage(self, response):
        products = response.css('div.single-product-area div.container div.row > div')        
        for product in products:            
            product_link = 'http://mezzohome.com/' + product.css('a::attr(href)').extract_first()
            product_name = product.css('h2 a::text').extract_first()
            product_price = product.css('div.product-carousel-price ins::text').extract_first().replace('Rs.','').strip()
            product_image = 'http://mezzohome.com/' + product.css('img::attr(src)').extract_first()
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
        
        productDesc = response.css('div[role="tabpanel"] div.tab-content').extract_first()
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

        with open('HCVID312.mezzohome.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})

        HCVID312_mezzohome_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
            
