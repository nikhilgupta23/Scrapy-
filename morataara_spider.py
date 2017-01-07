import scrapy
import csv
import json
import re
from html.parser import HTMLParser

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else '' for i in text])

class HCVID407_www_morataara_com_Spider(scrapy.Spider):
    name = "HCVID407.www.morataara.com"
    jsonData = []
    prodsSeen = []
    
    def start_requests(self):        
        link = 'http://www.morataara.com/wall-decor.html'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Wall Art'        
        yield request
        link = 'http://www.morataara.com/paper-products.html'
        request = scrapy.Request(url=link, callback = self.parsePage)
        request.meta['prod_category'] = 'Paper Products'
        request.meta['prod_no'] = 1
        yield request
        link = 'http://www.morataara.com/decor.html'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Decor'
        yield request
        link = 'http://www.morataara.com/storage-organization.html'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Storage'
        yield request
        link = 'http://www.morataara.com/lamps-7.html'
        request = scrapy.Request(url=link, callback = self.parsePage)
        request.meta['prod_category'] = 'Lamps'
        request.meta['prod_no'] = 1
        yield request
        link = 'http://www.morataara.com/garden.html'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Garden'
        yield request
        link = 'http://www.morataara.com/dining-serving.html'
        request = scrapy.Request(url=link, callback = self.parse)
        request.meta['prod_category'] = 'Dining & Serving'
        yield request
        link = 'http://www.morataara.com/bags-11.html'
        request = scrapy.Request(url=link, callback = self.parsePage)
        request.meta['prod_category'] = 'Bags'
        request.meta['prod_no'] = 1
        yield request
                                
    def parse(self, response):
        links = response.css('li.item')
        for link in links:            
            page = link.css('a::attr(href)').extract_first()
            request = scrapy.Request(url=page, callback = self.parsePage)            
            request.meta['prod_category'] = response.meta['prod_category'] + '|' + link.css('div.category-meta a::text').extract_first()
            request.meta['prod_no'] = 1
            yield request

    def parsePage(self, response):
        items = response.css('div.category-products li.item')   
        for item in items:            
            prod_link = item.css('a::attr(href)').extract_first()
            if prod_link not in HCVID407_www_morataara_com_Spider.prodsSeen:
                HCVID407_www_morataara_com_Spider.prodsSeen.append(prod_link)                
                request = scrapy.Request(url=prod_link, callback = self.parseProduct)
                request.meta['prod_link'] = prod_link                
                request.meta['prod_category'] = response.meta['prod_category']
                yield request
            else:
                return
        page = response.meta['prod_no'] + 1
        nextpage = response.request.url.split('?')[0] + '?p=' + str(page)
        request = scrapy.Request(url=nextpage, callback = self.parsePage)
        request.meta['prod_category'] = response.meta['prod_category']
        request.meta['prod_no'] = page
        yield request        
            
    def closed(self, reason):
        toWrite = {'data' : HCVID407_www_morataara_com_Spider.jsonData}
        with open('HCVID407.www.morataara.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)            
        
    def parseProduct(self, response):
        productLink = response.meta['prod_link']
        productCategory = response.meta['prod_category']
        productName = response.css('div.product-name h1::text').extract_first()
        productImage = response.css('div.product-image img::attr(src)').extract_first()
        productDesc = response.css('meta[name="description"]::attr(content)').extract_first()
        productPrice = response.css('span.price::text').extract_first().replace('Rs.','').strip()
        productSku = 'SKU-NA'
                            
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

        with open('HCVID407.www.morataara.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})

        HCVID407_www_morataara_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
