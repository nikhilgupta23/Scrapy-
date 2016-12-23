import scrapy
import csv
import json
import re
from html.parser import HTMLParser

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else '' for i in text])

class HCVID196_www_jaypore_com_Spider(scrapy.Spider):
    name = "HCVID196.www.jaypore.com"
    products_seen = []
    jsonData = []

    def closed(self, reason):
        toWrite = {'data' : HCVID196_www_jaypore_com_Spider.jsonData}
        with open('HCVID196.www.jaypore.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
    
    def start_requests(self):
        url = "https://www.jaypore.com/"
        yield scrapy.Request(url=url, callback=self.parse)
        
    def parse(self, response):
        x = response.css('li.nav-items')
        for columns in x:
            y = columns.css('section.topnav-column ul.topnav-menu-links')            
            for z in y:
                head_category = z.css('a h3::text').extract_first()
                list_items = z.css('li')
                for item in list_items:
                    page = item.css('a::attr(href)').extract_first()
                    sub_category = item.css('a::text').extract_first()
                    if page is not None:
                        request = scrapy.Request(url=page, callback = self.parsePage)
                        request.meta['category'] = str(head_category) + '|' + str(sub_category)
                        yield request
                        
    def parsePage(self, response):        
        products = response.css('li.proditems')        
        for product in products:            
            product_link = product.css('a::attr(href)').extract_first()
            if product_link not in HCVID196_www_jaypore_com_Spider.products_seen:
                HCVID196_www_jaypore_com_Spider.products_seen.append([product_link])
                request = scrapy.Request(url=product_link, callback=self.parseProduct)
                request.meta['product_link'] = product_link
                request.meta['category'] = response.meta['category']                
                yield request
                
    def parseProduct(self, response):
        productLink = response.meta['product_link']
        productCategory = response.meta['category']
        productName = response.css('h1.productName::text').extract_first()
        productImage = response.css('div.lftPanel img::attr(src)').extract_first()
        productDesc = ''
        productDescUl = response.css('ul.prdDisc span#prodDesc li')
        for li in productDescUl:
            productDesc += li.css('::text').extract_first() + '|'
        productDesc = productDesc[:-1]
        if not productDesc:
            productDescUl = response.css('ul.prdDisc span#prodDesc::text')
            for x in productDescUl:
                productDesc += x + '|'
            productDesc = productDesc[:-1]
        productPrice = response.css('span#dPrice::text').extract_first()
        productSku = response.xpath('//dd[last()]/text()').extract_first()

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

        with open('HCVID196.www.jaypore.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
        
        HCVID196_www_jaypore_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
            
