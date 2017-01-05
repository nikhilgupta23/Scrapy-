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

class HCVID401_www_rugberry_in_Spider(scrapy.Spider):
    name = "HCVID401.www.rugberry.in"
    jsonData = []
    
    def start_requests(self):        
        for x in range(1,12):
            link = 'http://www.rugberry.in/product-category/rugs/basic/page/'+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Rugs|Basic'
            yield request
        for x in range(1,13):
            link = 'http://www.rugberry.in/product-category/rugs/hand-carved/page/'+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Rugs|Hand Carved'
            yield request
        for x in range(1,3):
            link = 'http://www.rugberry.in/product-category/rugs/flora/page/'+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Rugs|Flora'
            yield request        
        for x in range(1,3):
            link = 'http://www.rugberry.in/product-category/rugs/kids/page/'+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Rugs|Kids'
            yield request        
        link = 'http://www.rugberry.in/product-category/rugs/luxor/'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Rugs|Luxor'
        yield request
        link = 'http://www.rugberry.in/product-category/rugs/textures/'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Rugs|Textures'
        yield request
        
                                
    def parse(self, response):
        items = response.css('div.products.row div.first.last.four')
        for item in items:            
            prod_link = item.css('a::attr(href)').extract_first()
            request = scrapy.Request(url=prod_link, callback = self.parseProduct)
            request.meta['prod_link'] = prod_link
            request.meta['prod_category'] = response.meta['prod_category']
            yield request

    def closed(self, reason):
        toWrite = {'data' : HCVID401_www_rugberry_in_Spider.jsonData}
        with open('HCVID401.www.rugberry.in.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)            
        
    def parseProduct(self, response):
        productLink = response.meta['prod_link']
        productCategory = response.meta['prod_category']
        productName = response.css('h1.page-title::text').extract_first()        
        productImage = response.css('div[itemprop="image"] img::attr(src)').extract_first()

        productDesc = response.css('li#tab-descriptionTab p::text').extract_first()
        if not productDesc:
            productDesc = response.css('div[itemprop="description"] p::text').extract_first()
 
        variantsJson = response.css('form.variations_form::attr(data-product_variations)').extract_first()
        variantsJson = json.loads(variantsJson.replace('&quot;','"'))
        for variant in variantsJson:
            productPrice = variant["display_price"]
            productSize = variant["attributes"]["attribute_pa_size"]
            productSku = variant["sku"]
            
            productDesc = re.sub('\n' ,'|',productDesc)
            productDesc = re.sub('\t','',productDesc)                             
            productDesc = re.sub('\r','',productDesc)
            productDesc = re.sub('[ ]+',' ',productDesc)
            productDesc = re.sub('(\| )+','|',productDesc)
            productDesc = re.sub('\|+','|',productDesc)
            productDesc = productDesc.strip('|')
            productDesc = productDesc.strip()        
            
            productCategory = productCategory.replace('"','``')                            
            productDesc = productDesc.replace('"','``')
            productName = productName.replace('"','``')

            productDesc = remove_non_ascii(productDesc)        
            productCategory = remove_non_ascii(productCategory)
            productName = remove_non_ascii(productName)

            with open('HCVID401.www.rugberry.in.csv', 'a', newline='') as csvfile:
                fieldnames = ['Title', 'Size', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
                writer.writerow({'Title': '"'+str(productName)+'"', 'Size': '"'+str(productSize)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
            
            HCVID401_www_rugberry_in_Spider.jsonData.append({'Title': productName, 'Size':productSize, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
