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

class HCVID402_www_casapop_com_Spider(scrapy.Spider):
    name = "HCVID402.www.casa-pop.com"    
    jsonData = []
    products_seen = []
    
    def closed(self, reason):
        toWrite = {'data' : HCVID402_www_casapop_com_Spider.jsonData}
        with open('HCVID402.www.casa-pop.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
    
    def start_requests(self):
        url = "http://www.casa-pop.com/"
        yield scrapy.Request(url=url, callback=self.parse)
        
    def parse(self, response):
        x = response.css('ul#nav li.level0')
        for columns in x:
            name = columns.css('a.level-top span::text').extract_first()
            if name == 'Home & Living' or name == 'Furniture':
                prod_cat_head = name + '|'
                cats = columns.css('span.heading-cat a')
                for cat in cats:
                    page = cat.css('::attr(href)').extract_first()
                    if page == 'http://www.casa-pop.com/lifestyle/wallpaper':
                        continue
                    prod_cat = prod_cat_head + cat.css('::text').extract_first()
                    request = scrapy.Request(url=page, callback = self.parsePage)
                    request.meta['prod_category'] = prod_cat
                    request.meta['pageno'] = 1
                    yield request
                        
    def parsePage(self, response):        
        products = response.css('li.item.last')        
        for product in products:            
            product_link = product.css('a::attr(href)').extract_first()
            if product_link not in HCVID402_www_casapop_com_Spider.products_seen:
                HCVID402_www_casapop_com_Spider.products_seen.append(product_link)
                request = scrapy.Request(url=product_link, callback=self.parseProduct)
                request.meta['prod_link'] = product_link
                request.meta['prod_category'] = response.meta['prod_category']      
                yield request
            else:
                return
        page = response.meta['pageno'] + 1
        nextpage = response.request.url.split('?')[0] + '?p=' + str(page)
        request = scrapy.Request(url=nextpage, callback = self.parsePage)
        request.meta['prod_category'] = response.meta['prod_category']
        request.meta['pageno'] = page
        yield request        
                
    def parseProduct(self, response):
        productLink = response.meta['prod_link']
        productCategory = response.meta['prod_category']
        productName = response.css('h1::text').extract_first()
        productImage = response.css('p.product-image img::attr(src)').extract_first()
        productDesc = response.css('div.description-block').extract_first()
        if not productDesc:
            productDesc = 'NA'
        else:
            productDesc = strip_tags(productDesc)
        productPrice = response.css('span.price::text').extract_first().replace('₹','').strip()
        productSku = strip_tags(response.css('div.sku').extract_first()).replace('SKU:','').strip()

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

        with open('HCVID402.www.casa-pop.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
        
        HCVID402_www_casapop_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
            
