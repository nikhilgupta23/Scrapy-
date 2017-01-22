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

class HCVID281_www_wudapple_com_Spider(scrapy.Spider):
    name = "HCVID281.www.wudapple.com"
    products_seen = []
    jsonData = []

    def closed(self, reason):
        toWrite = {'data' : HCVID281_www_wudapple_com_Spider.jsonData}
        with open('./json/HCVID281.www.wudapple.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
    
    def start_requests(self):
        url = "http://wudapple.com/webshop/"
        yield scrapy.Request(url=url, callback=self.parse)
        
    def parse(self, response):        
        x = response.css('div#menu-category-wall div.span10 div.span2 a')        
        for columns in x:
            head_category = columns.css('::text').extract_first()
            page = columns.css('::attr(href)').extract_first()
            request = scrapy.Request(url=page + '&page=1', callback = self.parsePage)
            request.meta['pagenum'] = 1
            request.meta['category'] = str(head_category)
            yield request                            

    def parsePage(self, response):
        products = response.css('div.product-list > div.span')
        if not products:
            return
        else:
            for product in products:            
                product_name = product.css('div.name a::text').extract_first()
                product_link = product.css('div.image a::attr(href)').extract_first()
                request = scrapy.Request(url=product_link, callback=self.parseProduct)
                request.meta['product_link'] = product_link                
                request.meta['product_name'] = product_name
                request.meta['product_category'] = response.meta['category']
                yield request
            nextpage = response.meta['pagenum'] + 1            
            product_link = response.request.url[:response.request.url.index('&page=')] + '&page=' + str(nextpage) + '/'
            request = scrapy.Request(url=product_link, callback=self.parsePage)
            request.meta['category'] = response.meta['category']
            request.meta['pagenum'] = nextpage
            yield request
                
    def parseProduct(self, response):
        productLink = response.meta['product_link']
        productCategory = response.meta['product_category']        
        productName = response.meta['product_name']
        productImage = response.css('div.image a::attr(href)').extract_first()
        
        productPrice = response.css('div.price::text').extract_first()
        if productPrice:
            productPrice = productPrice.replace('₹','').strip()
        else:
            productPrice = 'NA'

        productDesc = response.css('div#tab-description article').extract_first()
        productDesc = strip_tags(productDesc)
        if not productDesc:
            productDesc = 'NA'

        productInfos = response.css('div.description::text').extract()
        productSku = ''
        for info in productInfos:            
            if len(info.strip()) > 0:
                productSku = info.strip()
                break

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

        with open('HCVID281.www.wudapple.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})

        HCVID281_www_wudapple_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
            
