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

class HCVID191_socktail_com_Spider(scrapy.Spider):
    name = "HCVID191.socktail.com"
    jsonData = []
    
    def start_requests(self):
        for x in range(1,5):
            link = 'http://socktail.com/shopby/kids-furniture?pg='+str(x)
            yield scrapy.Request(url=link, callback = self.parse)
        for x in range(1,83):
            link = 'http://socktail.com/shopby/home-furniture?pg='+str(x)
            yield scrapy.Request(url=link, callback = self.parse)
        for x in range(1,4):
            link = 'http://socktail.com/shopby/garden-and-outdoor-furniture?pg='+str(x)
            yield scrapy.Request(url=link, callback = self.parse)
        for x in range(1,9):
            link = 'http://socktail.com/shopby/home-office-furniture?pg='+str(x)
            yield scrapy.Request(url=link, callback = self.parse)
        for x in range(1,32):
            link = 'http://socktail.com/shopby/accessories?pg='+str(x)
            yield scrapy.Request(url=link, callback = self.parse)
        for x in range(1,17):
            link = 'http://socktail.com/shopby/socktail-specials?pg='+str(x)
            yield scrapy.Request(url=link, callback = self.parse)
        
    def parse(self, response):        
        items = response.css('div.category_isotope_item')    
        for item in items:            
            prod_link = 'http://socktail.com/' + str(item.css('div.d_block a::attr(href)').extract_first())
            prod_name = item.css('a.second_font.sc_hover::text').extract_first()
            prod_price = str(item.css('b.scheme_color::text').extract_first()).replace('Rs','').strip()
            
            request = scrapy.Request(url=prod_link, callback = self.parseProduct)
            request.meta['prod_link'] = prod_link                
            request.meta['prod_name'] = prod_name
            request.meta['prod_price'] = prod_price            
            yield request

    def closed(self, reason):
        toWrite = {'data' : HCVID191_socktail_com_Spider.jsonData}
        with open('HCVID191.socktail.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
        
    def parseProduct(self, response):        
        productLink = response.meta['prod_link']
        productName = response.meta['prod_name']
        productPrice = response.meta['prod_price']
        productImage = response.css('img#zoom::attr(src)').extract_first()        
        productSku = response.css('ul.m_bottom_14 li.m_bottom_3:last-child span.fw_light::text').extract_first()
        productCategory = ''
        categoryParts = response.css('div.breadcrumbs div.container a::text').extract()
        for part in categoryParts:
            productCategory += part + '|'
        productCategory = productCategory[:-1]
        productDesc = ''
        descParts = response.css('div#tab1 p').extract()
        for part in descParts:            
            productDesc += strip_tags(part).strip() + '|'
        productDesc = productDesc[:-1]
        productDesc = productDesc.strip()                

        productCategory = productCategory.replace('"','``')        
        productDesc = re.sub('\n' ,'|',productDesc)
        productDesc = re.sub('\t','',productDesc)                             
        productDesc = re.sub('\r','',productDesc)
        productDesc = re.sub('[ ]+',' ',productDesc)
        productDesc = re.sub('(\| )+','|',productDesc)
        productDesc = re.sub('\|+','|',productDesc)
        try:
            productDesc = productDesc[1:] if productDesc[0] == '|' else productDesc
        except:
            pass
        productDesc = productDesc.replace('"','``')
        productName = productName.replace('"','``')
        
        productDesc = remove_non_ascii(productDesc)        
        productCategory = remove_non_ascii(productCategory)
        productName = remove_non_ascii(productName)
                
        with open('HCVID191.socktail.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
        
        HCVID191_socktail_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
