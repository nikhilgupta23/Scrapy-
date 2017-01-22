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

class HCVID269_www_pinklay_com_Spider(scrapy.Spider):
    name = "HCVID269.www.pinklay.com"
    products_seen = []
    jsonData = []

    def closed(self, reason):
        toWrite = {'data' : HCVID269_www_pinklay_com_Spider.jsonData}
        with open('./json/HCVID269.www.pinklay.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
    
    def start_requests(self):
        url = "http://www.pinklay.com/"
        yield scrapy.Request(url=url, callback=self.parse)
        
    def parse(self, response):        
        x = response.css('div#mega-menu-wrap-main_navigation ul#mega-menu-main_navigation > li')        
        for columns in x:
            head_category = columns.css('a::text').extract_first()
            if head_category != 'New Arrivals' and head_category != 'SALE':
                list_items = columns.css('ul.mega-sub-menu li')                
                for item in list_items:
                    page = item.css('a::attr(href)').extract_first()
                    sub_category = item.css('a::text').extract_first()                            
                    if page is not None:
                        print(page)
                        request = scrapy.Request(url=page+'/page/1/', callback = self.parsePage)
                        request.meta['pagenum'] = 1
                        request.meta['category'] = str(head_category) + '|' + str(sub_category)
                        yield request                            

    def parsePage(self, response):
        products = response.css('ul#products > li')
        if not products:
            return
        else:
            for product in products:            
                product_link = product.css('div.product-details h3 a::attr(href)').extract_first()
                product_name = product.css('div.product-details h3 a::text').extract_first()
                product_image = product.css('div.first-image img::attr(src)').extract_first()
                request = scrapy.Request(url=product_link, callback=self.parseProduct)
                request.meta['product_link'] = product_link
                request.meta['product_image'] = product_image
                request.meta['product_name'] = product_name
                request.meta['product_category'] = response.meta['category']
                yield request
            nextpage = response.meta['pagenum'] + 1
            product_link = ''
            if not '/page' in response.request.url:
                product_link = response.request.url[:response.request.url.rfind(str(response.meta['pagenum']))] + '/page/' + str(nextpage) + '/'
            else:
                product_link = response.request.url[:response.request.url.rfind(str(response.meta['pagenum']))] + '/' + str(nextpage) + '/'
            request = scrapy.Request(url=product_link, callback=self.parsePage)
            request.meta['category'] = response.meta['category']
            request.meta['pagenum'] = nextpage
            yield request
                
    def parseProduct(self, response):
        productLink = response.meta['product_link']
        productCategory = response.meta['product_category']
        productImage = response.meta['product_image']
        productName = response.meta['product_name']
        productMerchant = 'NA'
        productPrice = response.css('h3.price span.amount::text').extract_first()
        if productPrice:
            productPrice = productPrice.replace('Rs.','').strip()
        else:
            productPrice = 'NA'

        productDesc = response.css('div.product-short').extract_first()
        if productDesc:
            productDesc = strip_tags(productDesc)        

        additional = response.css('table.shop_attributes').extract_first()
        if not productDesc:
            productDesc = strip_tags(additional)
        else:
            productDesc += '|' + strip_tags(additional)

        productSku = response.css('div.entry-summary form.cart button[type="submit"]::attr(data-product_id)').extract_first()
        if not productSku:
            productSku = response.css('div.yith-wcwl-add-button a::attr(data-product-id)').extract_first()
        
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

        with open('HCVID269.www.pinklay.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})

        HCVID269_www_pinklay_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': productMerchant})
            
