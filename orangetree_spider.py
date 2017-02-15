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

class HCVID441_www_orangetree_co_in_Spider(scrapy.Spider):
    name = "HCVID441.www.orangetree.co.in"
    products_seen = []
    jsonData = []

    def closed(self, reason):
        toWrite = {'data' : HCVID441_www_orangetree_co_in_Spider.jsonData}
        with open('./json/HCVID441.www.orangetree.co.in.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
    
    def start_requests(self):
        url = "http://www.orangetree.co.in/"
        yield scrapy.Request(url=url, callback=self.parse)
        
    def parse(self, response):        
        page = 'http://www.orangetree.co.in/lighting-online/table-lamps.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/lighting-online/study-lamps.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/lighting-online/hanging-lamps.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/lighting-online/cluster-chandelier.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/lighting-online/floor-lamps.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/lighting-online/wall-lamps.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/lighting-online/lanterns-decorative-lights.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/lighting-online/lamp-shades.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/lighting-online/living-room-floor-lamps.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/lighting-online/dining-room-floor-lamps.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/lighting-online/bedroom-floor-lamps.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/lighting-online/living-room-table-lamps.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/lighting-online/dining-room-table-lamps.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/lighting-online/bedroom-table-lamps.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/lighting-online/living-room-hanging-lamps.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/lighting-online/bedroom-hanging-lamps.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/lighting-online/dining-room-hanging-lamps.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/lighting-online/bedside-lamps.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/lighting-online/tea-lights.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/lighting-online/tripod-lamps.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/home-decor/mirrors.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/home-decor/photoframes.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/home-decor/vases.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/home-decor/wall-decor.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/home-decor/table-clocks.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/accent-furniture/designer-side-tables.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/accent-furniture/wooden-stools.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/accent-furniture/wall-shelves.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request
        page = 'http://www.orangetree.co.in/retro.html'
        page = page + '?p=1'        
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['pagenum'] = 1
        yield request

    def parsePage(self, response):
        products = response.css('div.category-products li.item')
        product_category = ''
        product_categorys = response.css('div.breadcrumbs ul').extract_first()
        product_category = strip_tags(product_categorys).replace('|','').strip().replace('/','|').replace(' ','').replace('\n','').replace('Home|','')        
        for product in products:
            product_link = product.css('a::attr(href)').extract_first()
            product_image = product.css('a.product-image img::attr(src)').extract_first()
            product_name = product.css('h2.product-name a::text').extract_first()
            product_price = product.css('span.price::text').extract_first().replace('Rs.','').strip()            
                    
            request = scrapy.Request(url=product_link, callback=self.parseProduct)
            request.meta['product_link'] = product_link
            request.meta['product_image'] = product_image
            request.meta['product_price'] = product_price
            request.meta['product_name'] = product_name
            request.meta['product_category'] = product_category 
            yield request
            
    def parseProduct(self, response):
        productLink = response.meta['product_link']
        productCategory = response.meta['product_category']
        productImage = response.meta['product_image']        
        productPrice = response.meta['product_price']
        productName = response.meta['product_name']
        
        productDesc = response.css('table#product-attribute-specs-table').extract_first()        
        if not productDesc:
            productDesc = 'NA'
        else:
            productDesc = strip_tags(productDesc)
            
        productSku = strip_tags(response.css('div.add-to-box p').extract_first().replace('SKU Code','')).replace(':','').strip()

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

        with open('HCVID441.www.orangetree.co.in.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
        
        HCVID441_www_orangetree_co_in_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
            
