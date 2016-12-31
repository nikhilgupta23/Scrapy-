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
        
class HCVID289_thehumbletree_com_Spider(scrapy.Spider):
    name = "HCVID289.thehumbletree.com"
    jsonData = []
    
    def start_requests(self):
        for x in range(1,3):
            link = 'https://thehumbletree.com/product-category/lamps-lighting/page/'+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            yield request
        for x in range(1,3):
            link = 'https://thehumbletree.com/product-category/home-decor/page/'+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            yield request
        for x in range(1,4):
            link = 'https://thehumbletree.com/product-category/seating-furniture/page/'+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            yield request
        for x in range(1,5):
            link = 'https://thehumbletree.com/product-category/tables-furniture/page/'+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            yield request
        link = 'https://thehumbletree.com/product-category/bar-furniture/'
        request = scrapy.Request(url=link, callback = self.parse)        
        yield request
        link = 'https://thehumbletree.com/product-category/bookshelf-furniture/'
        request = scrapy.Request(url=link, callback = self.parse)
        yield request
        link = 'https://thehumbletree.com/product-category/chest-of-drawers/'
        request = scrapy.Request(url=link, callback = self.parse)
        yield request
        link = 'https://thehumbletree.com/product-category/tallboy/'
        request = scrapy.Request(url=link, callback = self.parse)
        yield request
        link = 'https://thehumbletree.com/product-category/trunks-furniture/'
        request = scrapy.Request(url=link, callback = self.parse)
        yield request
                                
    def parse(self, response):        
        items = response.css('ul#products-grid li')
        for item in items:
            prod_link = item.css('div.product_thumbnail_wrapper a::attr(href)').extract_first()
            prod_image = item.css('div.product_thumbnail_wrapper img::attr(src)').extract_first()
            prod_price = item.css('span.price span.amount::text').extract_first()
            if not prod_price:
                prod_price = 'NA'
            else:
                prod_price = prod_price.replace('₹','').strip()
            request = scrapy.Request(url=prod_link, callback = self.parseProduct)
            request.meta['prod_link'] = prod_link
            request.meta['prod_image'] = prod_image
            request.meta['prod_price'] = prod_price            
            yield request

    def closed(self, reason):
        toWrite = {'data' : HCVID289_thehumbletree_com_Spider.jsonData}
        with open('HCVID289.thehumbletree.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
        
    def parseProduct(self, response):        
        productLink = response.meta['prod_link']
        productImage = response.meta['prod_image']
        productPrice = response.meta['prod_price']
        productName = response.css('h1.product_title::text').extract_first()
        productSku = response.css('span.sku_wrapper span.sku::text').extract_first()
        productCategories = response.css('nav.woocommerce-breadcrumb a::text').extract()        
        productCategory = ''
        for catnum in range(1,len(productCategories)):
            productCategory += productCategories[catnum] + '|'
        productCategory = productCategory.strip('|')
        productDesc = response.css('div.product_description p::text').extract_first()

        attributes = response.css('table.shop_attributes tr')
        for att in attributes:
            if not productDesc:
                productDesc = strip_tags(att.css('th').extract_first()) + ' : ' + strip_tags(att.css('td').extract_first()) + '|'
            else:
                productDesc += strip_tags(att.css('th').extract_first()) + ' : ' + strip_tags(att.css('td').extract_first()) + '|'
        
        productCategory = productCategory.replace('"','``')
        productDesc = productDesc.strip('|')
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

        with open('HCVID289.thehumbletree.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
            
        HCVID289_thehumbletree_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
        
