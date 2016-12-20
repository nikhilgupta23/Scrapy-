import scrapy
import csv
import json
import re
from html.parser import HTMLParser

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else '' for i in text])

class HCVID238_serendipitydelhi_com_Spider(scrapy.Spider):
    name = "HCVID238.serendipity.delhi.com"
    jsonData = []
    
    def start_requests(self):
        for x in range(1,3):
            link = 'https://serendipitydelhi.com/collections/cushions?page='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Cushions'
            yield request
        for x in range(1,4):
            link = 'https://serendipitydelhi.com/collections/furniture?page='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Furniture'
            yield request
        for x in range(1,4):
            link = 'https://serendipitydelhi.com/collections/baby-bedding?page='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Baby Bedding'
            yield request
        for x in range(1,3):
            link = 'https://serendipitydelhi.com/collections/home-decor?page='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Wall Art'
            yield request
        for x in range(1,3):
            link = 'https://serendipitydelhi.com/collections/home-page-collection-2?page='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Featured Products'
            yield request
        link = 'https://serendipitydelhi.com/collections/cotton-bedding'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Cotton Bedding'
        yield request
        link = 'https://serendipitydelhi.com/collections/table-linen'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Table Linen'
        yield request
        link = 'https://serendipitydelhi.com/collections/toys'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Toys'
        yield request
        
    def parse(self, response):        
        items = response.css('li.collection__grid-item')
        for item in items:
            prod_link = 'https://serendipitydelhi.com/' + item.css('a.collection__product-link::attr(href)').extract_first()
            request = scrapy.Request(url=prod_link, callback = self.parseProduct)
            request.meta['prod_link'] = prod_link              
            request.meta['prod_category'] = response.meta['prod_category']
            yield request

    def closed(self, reason):
        toWrite = {'data' : HCVID238_serendipitydelhi_com_Spider.jsonData}
        with open('HCVID238.serendipity.delhi.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)

    @staticmethod
    def getImage(scripts, vId):
        for script in scripts:
                if "productJson:" in script:                    
                    l = script.split('\n')                    
                    for x in l:                        
                        if "productJson:" in x:
                            x = x.replace('productJson:','')
                            x = x.strip()
                            x = x[:-1]
                            j = (json.loads(x))["variants"]                            
                            for v in j:
                                if str(v["id"]) == vId:
                                    try:
                                        return v["featured_image"]["src"]
                                    except TypeError:
                                        return 'NA'
                                        
    def parseProduct(self, response):        
        partialProductLink = response.meta['prod_link']
        productCategory = response.meta['prod_category']
                    
        descParts = response.css('div.product__description').extract_first()
        productDesc = re.sub('<[^>]*>', '', descParts)

        productCategory = productCategory.replace('"','``')        
        productDesc = re.sub('\n' ,'|',productDesc)
        productDesc = re.sub('\t','',productDesc)                             
        productDesc = re.sub('\r','',productDesc)
        productDesc = re.sub('[ ]+',' ',productDesc)
        productDesc = re.sub('(\| )+','|',productDesc)
        productDesc = re.sub('\|+','|',productDesc)
        productDesc = productDesc.replace('"','``').strip('|')

        productDesc = remove_non_ascii(productDesc)        
        productCategory = remove_non_ascii(productCategory)

        content = response.css('script[type=text\/javascript]').extract_first()
        data = json.loads(re.search('var meta = (.*?);', content).group(1))
        productMerchant = data["product"]["vendor"]
        for variant in data["product"]["variants"]:
            productPrice = variant["price"]
            productName = variant["name"]
            productSku = variant["sku"]
            if not productSku:
                productSku = 'SKU-NA'
            productLink = partialProductLink + '?variant=' + str(variant["id"])
            productImage = HCVID238_serendipitydelhi_com_Spider.getImage(response.css('script').extract(), str(variant["id"]))                        
            productName = productName.replace('"','``')        
            productName = remove_non_ascii(productName)
                
            with open('HCVID238.serendipity.delhi.com.csv', 'a', newline='') as csvfile:
                fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
                writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"'+str(productMerchant)+'"'})
        
            HCVID238_serendipitydelhi_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': productMerchant})
