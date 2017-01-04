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

class HCVID195_www_woodenstreet_com_Spider(scrapy.Spider):
    name = "HCVID195.www.woodenstreet.com"
    jsonData = []
    
    def start_requests(self):
        link = 'https://www.woodenstreet.com/dining-furniture'
        request = scrapy.Request(url=link, callback = self.parseCat)        
        yield request
        link = 'https://www.woodenstreet.com/kids-furniture'
        request = scrapy.Request(url=link, callback = self.parseCat)        
        yield request
        link = 'https://www.woodenstreet.com/living-room-furniture'
        request = scrapy.Request(url=link, callback = self.parseCat)        
        yield request
        link = 'https://www.woodenstreet.com/storage-furniture'
        request = scrapy.Request(url=link, callback = self.parseCat)
        yield request
        link = 'https://www.woodenstreet.com/study-room-furniture'
        request = scrapy.Request(url=link, callback = self.parseCat)
        yield request
        link = 'https://www.woodenstreet.com/bedroom-furniture'
        request = scrapy.Request(url=link, callback = self.parseCat)
        yield request

    def parseCat(self, response):
        cats = response.css('div.allcategory a::attr(href)').extract()
        for cat in cats:
            link = 'https://www.woodenstreet.com/' + cat + '?page=1'
            request = scrapy.Request(url=link, callback = self.parsePages)
            request.meta['page'] = 1
            yield request

    def parsePages(self, response):
        if response.css('div.product-list').extract_first():
            articles = response.css('div.product-list article')
            for article in articles:                
                prod_link = article.css('a::attr(href)').extract_first()
                if not prod_link:
                    continue
                request = scrapy.Request(url=prod_link, callback = self.parseProduct)
                request.meta['prod_link'] = prod_link
                yield request
            page = response.meta['page'] + 1
            nextpage = response.request.url.split('?')[0] + '?page=' + str(page)
            next_request = scrapy.Request(url=nextpage, callback = self.parsePages)
            next_request.meta['page'] = page
            yield next_request        

    def closed(self, reason):
        toWrite = {'data' : HCVID195_www_woodenstreet_com_Spider.jsonData}
        with open('HCVID195.www.woodenstreet.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
        
    def parseProduct(self, response):        
        productLink = response.meta['prod_link']
        productImage = response.css('li img[itemprop="image"]::attr(src)').extract_first()
        productName = strip_tags(response.css('h1.heading.hemedium').extract_first())

        productCategories = response.css('div.breadcrumbs li a::text').extract()
        productCategory = ''
        for catno in range(1,len(productCategories)):
            productCategory += productCategories[catno] + '|'
        productCategory = productCategory.strip('|')
                
        productDesc = response.css('article#detail').extract_first()
        info = response.css('div.text p').extract()
        inform = ''
        for infono in range(1,len(info)):
            inform += info[infono] + '|'
        inform = inform.strip('|')        
        if not productDesc:
            productDesc = strip_tags(inform)
        else:
            productDesc = strip_tags(productDesc) + '|' + strip_tags(inform)

        productDesc = productDesc.replace('Never miss our special offers, events or promotions.','')
        productSku = response.css('div.text p span:last-child::text').extract_first()

        productPrice = ''
        if not response.css('p.coupon_our_price::text').extract_first():
            productPrice = response.css('p.retprice span.price_container::text').extract_first().replace('Rs','').strip()
        else:
            productPrice = response.css('p.coupon_our_price::text').extract_first().replace('Our Price Rs','').strip()

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
 
        with open('HCVID195.www.woodenstreet.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
            
        HCVID195_www_woodenstreet_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})        
