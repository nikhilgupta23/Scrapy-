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
            if columns.css('a::text').extract_first() == 'HOME & DECOR':
                y = columns.css('section.topnav-column ul.topnav-menu-links')            
                for z in y:
                    head_category = z.css('a h3::text').extract_first()
                    list_items = z.css('li')
                    for item in list_items:                        pri
                        page = item.css('a::attr(href)').extract_first()
                        sub_category = item.css('a::text').extract_first()
                        if page is not None:
                            request = scrapy.Request(url=page, callback = self.parsePage)
                            request.meta['category'] = str(head_category) + '|' + str(sub_category)
                            yield request
                        
    def parsePage(self, response):
        page = response.request.url.split('?')[0]
        idnum = re.match('.*?([0-9]+)$', page).group(1)
        product_link = 'https://www.jaypore.com/shop_sorting_ajax_test.php?shopId=' + idnum + '&sort=featured&p=1&mobile=false&brand_ids=0&sale_only=0'
        request = scrapy.Request(url=product_link, callback=self.parseOthers)
        request.meta['category'] = response.meta['category']
        request.meta['pagenum'] = 1
        request.meta['idnum'] = idnum
        yield request

    def parseOthers(self, response):
        products = json.loads(response.body_as_unicode())
        if len(products) == 0:
            return        
        for product in products:            
            product_link = product["url"]
            if product_link not in HCVID196_www_jaypore_com_Spider.products_seen:
                HCVID196_www_jaypore_com_Spider.products_seen.append([product_link])
                request = scrapy.Request(url=product_link, callback=self.parseProduct)
                request.meta['product_link'] = product_link
                request.meta['category'] = response.meta['category']                
                yield request
        nextpage = response.meta['pagenum'] + 1
        idnum = response.meta['idnum']
        product_link = 'https://www.jaypore.com/shop_sorting_ajax_test.php?shopId=' + idnum + '&sort=featured&p=' + str(nextpage) + '&mobile=false&brand_ids=0&sale_only=0'
        request = scrapy.Request(url=product_link, callback=self.parseOthers)
        request.meta['category'] = response.meta['category']
        request.meta['pagenum'] = nextpage
        request.meta['idnum'] = idnum
        yield request
                
    def parseProduct(self, response):
        productLink = response.meta['product_link']
        productCategory = response.meta['category']
        productName = response.css('h1.productName::text').extract_first()
        productImage = response.css('div.lftPanel img::attr(src)').extract_first()
        productDesc = response.css('ul.prdDisc span#prodDesc').extract_first()
        if not productDesc:
            productDesc = 'NA'
        else:
            productDesc = strip_tags(productDesc)
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
            
