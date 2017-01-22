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

class HCVID282_www_cobblestreet_com_Spider(scrapy.Spider):
    name = "HCVID282.www.cobble-street.com"
    products_seen = []
    jsonData = []

    def closed(self, reason):
        toWrite = {'data' : HCVID282_www_cobblestreet_com_Spider.jsonData}
        with open('./json/HCVID282.www.cobble-street.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
    
    def start_requests(self):
        link = 'http://www.cobble-street.com/sculptures?page=1'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['product_category'] = 'Sculptures'
        request.meta['pagenum'] = 1
        yield request
        link = 'http://www.cobble-street.com/paintings/landscape?page=1'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['product_category'] = 'Paintings|Landscape'
        request.meta['pagenum'] = 1
        yield request
        link = 'http://www.cobble-street.com/paintings/abstract?page=1'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['product_category'] = 'Paintings|Abstract'
        request.meta['pagenum'] = 1
        yield request
        link = 'http://www.cobble-street.com/paintings/figurative?page=1'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['product_category'] = 'Paintings|Figurative'
        request.meta['pagenum'] = 1
        yield request
        link = 'http://www.cobble-street.com/paintings/still-life?page=1'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['product_category'] = 'Paintings|Still Life'
        request.meta['pagenum'] = 1
        yield request
        link = 'http://www.cobble-street.com/paintings/vastu?page=1'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['product_category'] = 'Paintings|Vastu'
        request.meta['pagenum'] = 1
        yield request
        link = 'http://www.cobble-street.com/paintings/rural-art?page=1'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['product_category'] = 'Paintings|Rural Art'
        request.meta['pagenum'] = 1
        yield request                            

    def parse(self, response):
        products = response.css('div.product-list div.col-lg-4.col-md-4.col-sm-4.col-xs-12')        
        if not products:
            return
        else:
            for product in products:            
                product_name = product.css('div.product-meta h3.name a::text').extract_first()
                product_link = product.css('div.image_container a::attr(href)').extract_first()
                product_image = product.css('div.image_container a img::attr(src)').extract_first()
                product_price = product.css('div.price::text').extract_first().replace('Price :','').replace('INR','').replace('/-','').strip()													
                request = scrapy.Request(url=product_link, callback=self.parseProduct)
                request.meta['product_link'] = product_link                
                request.meta['product_name'] = product_name
                request.meta['product_price'] = product_price
                request.meta['product_image'] = product_image
                request.meta['product_category'] = response.meta['product_category']
                yield request
            nextpage = response.meta['pagenum'] + 1            
            product_link = response.request.url[:response.request.url.index('?page=')] + '?page=' + str(nextpage)
            request = scrapy.Request(url=product_link, callback=self.parse)
            request.meta['product_category'] = response.meta['product_category']
            request.meta['pagenum'] = nextpage
            yield request
                
    def parseProduct(self, response):
        productLink = response.meta['product_link']
        productPrice = response.meta['product_price']
        productName = response.meta['product_name']
        productImage = response.meta['product_image']
        productCategory = response.meta['product_category']        
        
        productDesc = response.css('div.product-info div.col-lg-7.col-md-7.col-sm-7.col-xs-12:last-child div.description').extract_first()
        productDesc = strip_tags(productDesc)
        if not productDesc:
            productDesc = 'NA'
        
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

        productSku = productDesc.strip('Code No.:|').split('|')[0]
        productDesc = 'Artist:|' + response.css('div.product-info div.col-lg-7.col-md-7.col-sm-7.col-xs-12:last-child a::text').extract_first() + '|' +productDesc
        
        with open('HCVID282.www.cobble-street.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})

        HCVID282_www_cobblestreet_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
            
