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

class HCVID261_www_rainforestitaly_com_Spider(scrapy.Spider):
    name = "HCVID261.www.rainforestitaly.com"    
    jsonData = []
    
    def closed(self, reason):
        toWrite = {'data' : HCVID261_www_rainforestitaly_com_Spider.jsonData}
        with open('./json/HCVID261.www.rainforestitaly.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
    
    def start_requests(self):
        for x in range(1,3):
            link = 'http://www.rainforestitaly.com/bed-bedside/side-table?p=' + str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Table|Side Table'
            yield request
        link = 'http://www.rainforestitaly.com/tables/coffee-table'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Table|Coffee Table'
        yield request
        link = 'http://www.rainforestitaly.com/tables/center-table'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Table|Center Table'
        yield request
        link = 'http://www.rainforestitaly.com/tables/study-table'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Table|Study Table'
        yield request
        link = 'http://www.rainforestitaly.com/bed-bedside/beds'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Bed/Bedside|Beds'
        yield request
        link = 'http://www.rainforestitaly.com/bed-bedside/side-table'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Bed/Bedside|Side Table'
        yield request
        link = 'http://www.rainforestitaly.com/sofa-seating/accent-chair'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Sofa & Seating|Accent Chair'
        yield request
        link = 'http://www.rainforestitaly.com/sofa-seating/dining-chair'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Sofa & Seating|Dining Chair'
        yield request
        link = 'http://www.rainforestitaly.com/sofa-seating/sofa'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Sofa & Seating|Sofa'
        yield request
        link = 'http://www.rainforestitaly.com/storage/console'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Storage|Console'
        yield request
        link = 'http://www.rainforestitaly.com/storage/display-unit'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Storage|Display Unit'
        yield request
        link = 'http://www.rainforestitaly.com/storage/bar-unit'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Storage|Bar Unit'
        yield request
        link = 'http://www.rainforestitaly.com/art-and-mirror/mirrors'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Art & Mirrors|Mirrors'
        yield request
        
    def parse(self, response):        
        products = response.css('li.item.last')        
        for product in products:            
            product_link = product.css('a::attr(href)').extract_first()            
            request = scrapy.Request(url=product_link, callback=self.parseProduct)
            request.meta['prod_link'] = product_link
            request.meta['prod_category'] = response.meta['prod_category']      
            yield request
                
    def parseProduct(self, response):
        productLink = response.meta['prod_link']
        productCategory = response.meta['prod_category']
        productName = response.css('span.h1::text').extract_first()
        productImage = response.css('img#image-main::attr(src)').extract_first()
        productSku = 'SKU-NA'
        
        productDesc = response.css('div.padder div.std').extract_first()
        if not productDesc:
            productDesc = 'NA'
        else:
            productDesc = strip_tags(productDesc)

        productPrice = response.css('p.old-price span.price::text').extract_first()
        if not productPrice:
            productPrice = response.css('span.regular-price span.price::text').extract_first().replace('Rs','').strip()
        else:
            productPrice = productPrice.replace('Rs','').strip()
        
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

        with open('HCVID261.www.rainforestitaly.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})

        HCVID261_www_rainforestitaly_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
            
