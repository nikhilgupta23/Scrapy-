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
        
class HCVID233_zufolodesigns_com_Spider(scrapy.Spider):
    name = "HCVID233.zufolodesigns.com"
    jsonData = []
    
    def start_requests(self):
        for x in range(1,3):
            link = 'http://zufolodesigns.com/collections/cushions?view=all&page='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Cushions'
            yield request
        for x in range(1,3):
            link = 'http://zufolodesigns.com/collections/decor?view=all&page='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Decor'
            yield request
        for x in range(1,3):
            link = 'http://zufolodesigns.com/collections/dining?view=all&page='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Dining'
            yield request
        for x in range(1,3):
            link = 'http://zufolodesigns.com/collections/garden-outdoor?view=all&page='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Garden & Outdoor'
            yield request
        link = 'http://zufolodesigns.com/collections/lighting?view=all'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Lightning'
        yield request
        link = 'http://zufolodesigns.com/collections/rugs?view=all'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Rugs'
        yield request
        link = 'http://zufolodesigns.com/collections/throws?view=all'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Throws'
        yield request
        link = 'http://zufolodesigns.com/collections/candles?view=all'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Candles'
        yield request
        link = 'http://zufolodesigns.com/collections/furniture?view=all'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Furniture'
        yield request
        
                                
    def parse(self, response):        
        items = response.css('div.products-grid div.wow')
        for item in items:
            prod_link = 'http://zufolodesigns.com' + item.css('div.product-top div.product-image a::attr(href)').extract_first()
            prod_link = 'http://zufolodesigns.com/products/' + prod_link.rsplit('/', 1)[-1]
            prod_image = item.css('div.product-image a img::attr(src)').extract_first()
            request = scrapy.Request(url=prod_link, callback = self.parseProduct)
            request.meta['prod_link'] = prod_link
            request.meta['prod_image'] = prod_image
            request.meta['prod_category'] = response.meta['prod_category']
            yield request

    def closed(self, reason):
        toWrite = {'data' : HCVID233_zufolodesigns_com_Spider.jsonData}
        with open('HCVID233.zufolodesigns.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
        
    def parseProduct(self, response):        
        productLink = response.meta['prod_link']
        productImage = response.meta['prod_image']
        productCategory = response.meta['prod_category']
        productDesc = ''
        productDescs = response.css('div.short-description p').extract()
        for desc in productDescs:
            productDesc += strip_tags(desc) + '|'
        productDesc = re.sub('\n' ,'|',productDesc)
        productDesc = re.sub('\t','',productDesc)                             
        productDesc = re.sub('\r','',productDesc)
        productDesc = re.sub('[ ]+',' ',productDesc)
        productDesc = re.sub('(\| )+','|',productDesc)
        productDesc = re.sub('\|+','|',productDesc)        
        productDesc = productDesc.strip('|')
        productDesc = productDesc.strip()
        productDesc = remove_non_ascii(productDesc)        

        scripts = response.css('script[type=text\/javascript]').extract()
        for script in scripts:
            if 'var meta' in script:
                data = json.loads(re.search('var meta = (.*?);', script).group(1))
                productMerchant = data["product"]["vendor"]
                variants = data["product"]["variants"]
                for variant in variants:
                    productSku = variant["sku"]
                    productPrice = variant["price"]
                    productName = variant["name"]

                    productCategory = productCategory.replace('"','``')                            
                    productDesc = productDesc.replace('"','``')
                    productName = productName.replace('"','``')
                    
                    productCategory = remove_non_ascii(productCategory)
                    productName = remove_non_ascii(productName)

                    with open('HCVID233.zufolodesigns.com.csv', 'a', newline='') as csvfile:
                        fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
                        writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"'+str(productMerchant)+"'"})
        
                    HCVID233_zufolodesigns_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': productMerchant})
                break
        
