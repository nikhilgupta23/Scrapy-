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

class HCVID272_www_pinkapple_co_in_Spider(scrapy.Spider):
    name = "HCVID272.www.pinkapple.co.in"
    jsonData = []
    prodsSeen = []
    
    def closed(self, reason):
        toWrite = {'data' : HCVID272_www_pinkapple_co_in_Spider.jsonData}
        with open('./json/HCVID272.www.pinkapple.co.in.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
    
    def start_requests(self):
        link = 'http://pinkapple.co.in/wallart.html'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'WallArt'
        request.meta['pageno'] = 1
        yield request
        link = 'http://pinkapple.co.in/residential/blinds.html'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Residential|Blinds'
        request.meta['pageno'] = 1
        yield request
        link = 'http://pinkapple.co.in/residential/lighting.html'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Residential|Lightning'
        request.meta['pageno'] = 1
        yield request
        link = 'http://pinkapple.co.in/residential/furniture.html'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Residential|Furniture'
        request.meta['pageno'] = 1
        yield request
        link = 'http://pinkapple.co.in/residential/rugs-carpets.html'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Residential|Rugs/Carpets'
        request.meta['pageno'] = 1
        yield request
        link = 'http://pinkapple.co.in/residential/limited-edition.html'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Residential|Limited Edition'
        request.meta['pageno'] = 1
        yield request        
        
    def parse(self, response):    
        products = response.css('li.ma-item_slider')        
        for product in products:            
            product_link = product.css('div.images-container a::attr(href)').extract_first()
            if product_link in HCVID272_www_pinkapple_co_in_Spider.prodsSeen:
                break            
            request = scrapy.Request(url=product_link, callback=self.parseProduct)
            request.meta['prod_link'] = product_link
            request.meta['prod_category'] = response.meta['prod_category']
            yield request
        nextpageno = response.meta['pageno'] + 1
        nextpage = response.request.url.split('?')[0] + '?p=' + str(nextpageno)
        request = scrapy.Request(url=nextpage, callback = self.parse)
        request.meta['pageno'] = nextpageno
        request.meta['prod_category'] = response.meta['prod_category']
        yield request
                
    def parseProduct(self, response):
        productLink = response.meta['prod_link']

        productCategory = response.meta['prod_category']
        paras = response.css('div.std p').extract()
        for para in paras:
            x = strip_tags(para)
            if 'Category:' in x:
                productCategory += '|' + x.replace('Category:','').strip()
                break
                
        productName = response.css('div.product-name h1::text').extract_first()        
        productImage = response.css('p.product-image a::attr(href)').extract_first()
        productSku = productName[productName.find("(")+1:productName.find(")")]
        productName = productName[:productName.rfind('(')]
        
        productDesc = response.css('div.std').extract_first()
        if not productDesc:
            productDesc = 'NA'
        else:
            productDesc = strip_tags(productDesc)

        productPrice = response.css('div.price-box span.price::text').extract_first().replace('Rs','').strip()

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

        with open('HCVID272.www.pinkapple.co.in.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})

        HCVID272_www_pinkapple_co_in_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
            
