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

class HCVID169_www_artcollective_com_Spider(scrapy.Spider):
    name = "HCVID169.www.artcollective.com"
    jsonData = []
    
    def start_requests(self):
        for x in range(1,5):
            link = 'http://www.artcollective.com/collections/serigraphs?page='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Serigraphs'
            yield request
        for x in range(1,46):
            link = 'http://www.artcollective.com/collections/all-products?page='+str(x)
            request = scrapy.Request(url=link, callback = self.parse)
            request.meta['prod_category'] = 'Giclee Canvas Prints'
            yield request
                    
    def parse(self, response):
       items = response.css('div.objects')
       for item in items:            
            prod_link = 'http://www.artcollective.com/' + item.css('a::attr(href)').extract_first()
            prod_image = item.css('a img::attr(data-src)').extract_first()
            prod_name = item.css('span.title::text').extract_first()
            prod_sku = item.css('span[itemprop="sku"]::text').extract_first()
            request = scrapy.Request(url=prod_link, callback = self.parseProduct)
            request.meta['prod_link'] = prod_link
            request.meta['prod_image'] = prod_image
            request.meta['prod_name'] = prod_name
            request.meta['prod_sku'] = prod_sku
            request.meta['prod_category'] = response.meta['prod_category']
            yield request       

    def closed(self, reason):
        toWrite = {'data' : HCVID169_www_artcollective_com_Spider.jsonData}
        with open('HCVID169.www.artcollective.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
        
    def parseProduct(self, response):        
        productLink = response.meta['prod_link']
        productImage = response.meta['prod_image']
        productName = strip_tags(response.css('div.col-md-12 div.rasaleela').extract_first()).strip().replace('by',' by')        
        productCategory = response.meta['prod_category']
        productSku = response.css('p.vendor span::text').extract_first()
        if not productSku:
            productSku = response.css('p.sku span::text').extract_first()
        productDesc = strip_tags(response.css('div.description').extract_first())
        productPrice = response.css('span.current_price::text').extract_first().replace('Rs.','').strip()

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
 
        with open('HCVID169.www.artcollective.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
            
        HCVID169_www_artcollective_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})        
