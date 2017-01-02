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

class HCVID408_www_homeglamour_in_Spider(scrapy.Spider):
    name = "HCVID408.www.homeglamour.in"
    jsonData = []
    
    def start_requests(self):
        for x in range(1,4):
            link = 'https://homeglamour.in/collections/industrial-furniture-chair-stool?page='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Seating'
            yield request
        link = 'https://homeglamour.in/collections/industrial-furniture-tables'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Tables'
        yield request
        link = 'https://homeglamour.in/collections/industrial-furniture-storage'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Storage'
        yield request
                                
    def parse(self, response):        
        items = response.css('div.grid.grid--uniform div.grid__item')
        for item in items:
            prod_link = 'https://homeglamour.in' + item.css('a::attr(href)').extract_first()
            prod_image = item.css('div.product-card__image-wrapper img::attr(src)').extract_first()
            request = scrapy.Request(url=prod_link, callback = self.parseProduct)
            request.meta['prod_category'] = response.meta['prod_category']
            request.meta['prod_image'] = prod_image
            request.meta['prod_link'] = prod_link
            yield request            

    def closed(self, reason):
        toWrite = {'data' : HCVID408_www_homeglamour_in_Spider.jsonData}
        with open('HCVID408.www.homeglamour.in.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)

    def parseProduct(self, response):
        productLink = response.meta['prod_link']
        productCategory = response.meta['prod_category']
        productImage = response.meta['prod_image']

        productDesc = ''
        if response.css('div.description div#tabs-2').extract_first():
            productDesc = strip_tags(response.css('div.description div#tabs-2').extract_first())
        else:
            productDesc = strip_tags(response.css('div.description').extract_first())

        productDesc = re.sub('\n' ,'|',productDesc)
        productDesc = re.sub('\t','',productDesc)                             
        productDesc = re.sub('\r','',productDesc)
        productDesc = re.sub('[ ]+',' ',productDesc)
        productDesc = re.sub('(\| )+','|',productDesc)
        productDesc = re.sub('\|+','|',productDesc)        
        productDesc = productDesc.strip('|')
        productDesc = productDesc.strip()                        
        productDesc = productDesc.replace('"','``')        
        productDesc = remove_non_ascii(productDesc)

        scripts = response.css('script[type=text\/javascript]').extract()
        for script in scripts:
            if 'var meta' in script:
                data = json.loads(re.search('var meta = (.*?);', script).group(1))
                productMerchant = data["product"]["vendor"]
                variants = data["product"]["variants"]
                productCategory = productCategory + '|' + data["product"]["type"]
                for variant in variants:
                    productSku = variant["sku"]
                    if not productSku:
                        productSku = 'SKU-NA'
                        
                    productPrice = variant["price"]
                    productName = variant["name"]
                    
                    productCategory = productCategory.replace('"','``')
                    productName = productName.replace('"','``')
                    
                    productCategory = remove_non_ascii(productCategory)
                    productName = remove_non_ascii(productName)
        
                    with open('HCVID408.www.homeglamour.in.csv', 'a', newline='') as csvfile:
                        fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
                        writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"'+str(productMerchant)+'"'})
                        
                    HCVID408_www_homeglamour_in_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': productMerchant})
                break



        
