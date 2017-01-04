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

class HCVID400_elvy_com_Spider(scrapy.Spider):
    name = "HCVID400.elvy.com"
    jsonData = []
    
    def start_requests(self):        
        link = 'https://elvy.com/shop-by-category/bar'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Bar'
        yield request
        link = 'https://elvy.com/shop-by-category/serving'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Serving'
        yield request
        link = 'https://elvy.com/shop-by-category/decor'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Decor'
        yield request
        link = 'https://elvy.com/shop-by-category/office'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Office'
        yield request
        link = 'https://elvy.com/shop-by-category/travel'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Travel'
        yield request
        link = 'https://elvy.com/shop-by-category/outdoor'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Outdoor'
        yield request
        link = 'https://elvy.com/shop-by-category/bath'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Bath'
        yield request
        link = 'https://elvy.com/shop-by-category/junior'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Juniors'
        yield request    
                                
    def parse(self, response):
        items = response.css('ul.row.products li.item')
        for item in items:            
            prod_link = item.css('a::attr(href)').extract_first()
            prod_image = item.css('a img::attr(src)').extract_first()
            prod_name = item.css('h2.product-name a::text').extract_first()
            prod_price = item.css('span.price::text').extract_first().replace('₹','').strip()
            request = scrapy.Request(url=prod_link, callback = self.parseProduct)
            request.meta['prod_link'] = prod_link
            request.meta['prod_name'] = prod_name
            request.meta['prod_category'] = response.meta['prod_category']
            request.meta['prod_price'] = prod_price
            request.meta['prod_image'] = prod_image
            yield request

    def closed(self, reason):
        toWrite = {'data' : HCVID400_elvy_com_Spider.jsonData}
        with open('HCVID400.elvy.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)            
        
    def parseProduct(self, response):
        productLink = response.meta['prod_link']
        productCategory = response.meta['prod_category']
        productName = response.meta['prod_name']
        productPrice = response.meta['prod_price']        
        productImage = response.meta['prod_image']
        productDesc = response.css('div.std::text').extract_first()
        
        productSkuPos = 0
        skuFound = False
        productSku = ''
        productDetails = response.css('ul.prouctattributes li').extract()
        for detail in productDetails:
            if 'SKU' in detail:
                skuFound = True
                break
            productSkuPos = productSkuPos + 1
        if not skuFound:
            productSku = 'SKU-NA'
        else:
            productSku = response.css('ul.prouctattributes li::text').extract()[productSkuPos]        
                
        productDesc = re.sub('\n' ,'|',productDesc)
        productDesc = re.sub('\t','',productDesc)                             
        productDesc = re.sub('\r','',productDesc)
        productDesc = re.sub('[ ]+',' ',productDesc)
        productDesc = re.sub('(\| )+','|',productDesc)
        productDesc = re.sub('\|+','|',productDesc)
        productDesc = productDesc.replace('Product Description|','')
        productDesc = productDesc.strip('|')
        productDesc = productDesc.strip()        
        
        productCategory = productCategory.replace('"','``')                            
        productDesc = productDesc.replace('"','``')
        productName = productName.replace('"','``')

        productDesc = remove_non_ascii(productDesc)        
        productCategory = remove_non_ascii(productCategory)
        productName = remove_non_ascii(productName)

        with open('HCVID400.elvy.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})

        HCVID400_elvy_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
