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

class HCVID250_www_ediy_in_Spider(scrapy.Spider):
    name = "HCVID250.www.ediy.in"
    jsonData = []
    prodSeen = []
    
    def closed(self, reason):
        toWrite = {'data' : HCVID250_www_ediy_in_Spider.jsonData}
        with open('./json/HCVID250.www.ediy.in.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
    
    def start_requests(self):
        link = 'https://www.ediy.in/'
        request = scrapy.Request(url=link, callback = self.parse)
        yield request       
        
    def parse(self, response):
        x = response.css('ul.navigation-menu-items > li')        
        for columns in x:
            head_category = columns.css('a::text').extract_first().strip()
            y = columns.css('div.submenu-list > ul a')
            for z in y:                
                page = 'https://www.ediy.in' + z.css('::attr(href)').extract_first()
                sub_category = z.css('::text').extract_first().strip()
                if page is not None:
                    request = scrapy.Request(url=page, callback = self.parsePage)
                    request.meta['prod_category'] = str(head_category) + '|' + str(sub_category)
                    yield request
        page = 'https://www.ediy.in/accessories/puffys'
        request = scrapy.Request(url=page, callback = self.parsePage)
        request.meta['prod_category'] = 'Accessories|Puffy'
        yield request
        

    def parsePage(self, response):    
        products = response.css('ul.prd-list > li')
        if products:
            for product in products:
                product_link = 'https://www.ediy.in' + product.css('a::attr(href)').extract_first()
                if product_link in HCVID250_www_ediy_in_Spider.prodSeen:
                    continue
                HCVID250_www_ediy_in_Spider.prodSeen.append(product_link)
                request = scrapy.Request(url=product_link, callback=self.parseProduct)
                request.meta['prod_link'] = product_link
                request.meta['prod_image'] = 'https://www.ediy.in' + product.css('a img::attr(src)').extract_first()
                request.meta['prod_category'] = response.meta['prod_category']
                yield request
        else:
            products = response.css('div.allitems > div.itemunit')
            for product in products:
                product_link = 'https://www.ediy.in' + product.css('a::attr(href)').extract_first()
                if product_link in HCVID250_www_ediy_in_Spider.prodSeen:
                    continue
                HCVID250_www_ediy_in_Spider.prodSeen.append(product_link)
                request = scrapy.Request(url=product_link, callback=self.parseProduct)
                request.meta['prod_link'] = product_link
                request.meta['prod_image'] = 'https://www.ediy.in' + product.css('a img::attr(src)').extract_first()
                request.meta['prod_category'] = response.meta['prod_category']
                yield request
                
    def parseProduct(self, response):
        productLink = response.meta['prod_link']
        productImage = response.meta['prod_image']
        productCategory = response.meta['prod_category']
        productName = response.css('h2.decpro-title::text').extract_first()
        if not productName:
            productName = response.css('div.product-title::text').extract_first().strip()
        productSku = response.css('input[name="skuid"]::attr(value)').extract_first()
        if not productSku:
            productSku = 'SKU-NA'
        productDesc = response.css('table.tblspecification').extract_first()
        if not productDesc:
            productDesc = strip_tags(response.css('div.product-details-info').extract_first())
        else:
            productDesc = strip_tags(productDesc)

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

        productPrice = response.css('ul.price-view li p::text').extract_first()
        if not productPrice:
            productPrice = response.css('div.product-rate-block-actual::text').extract_first()
        if not productPrice:
            rows = response.css('div.price-table div.price-table-row')
            if rows:
                for row in rows:
                    productVariant = strip_tags(row.css('div.price-table-cell').extract_first()).strip()
                    productVariant = productVariant.replace('"','``')
                    
                    productPrice = row.css('div.price-table-cell:last-child::text').extract_first().replace('Rs.','').strip()                

                    with open('HCVID250.www.ediy.in.csv', 'a', newline='') as csvfile:
                        fieldnames = ['Title', 'Size', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
                        writer.writerow({'Title': '"'+str(productName)+'"', 'Size': '"'+str(productVariant)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
                        
                    HCVID250_www_ediy_in_Spider.jsonData.append({'Title': productName, 'Size':productVariant, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
            else:
                rows = response.css('div.product-rate-block-actual p')                
                for row in rows:
                    productVariant = row.css('label span::text').extract_first().strip()
                    productVariant = productVariant.replace('"','``')
                    productPrice = row.css('label::text').extract_first().replace('Rs.','').strip()                

                    with open('HCVID250.www.ediy.in.csv', 'a', newline='') as csvfile:
                        fieldnames = ['Title', 'Size', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
                        writer.writerow({'Title': '"'+str(productName)+'"', 'Size': '"'+str(productVariant)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
                        
                    HCVID250_www_ediy_in_Spider.jsonData.append({'Title': productName, 'Size':productVariant, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
                                
        else:
            productPrice = productPrice.replace('Rs.','').replace('Today\'s Price','').replace('Family Offer','').strip()
            productVariant = 'NA'

            with open('HCVID250.www.ediy.in.csv', 'a', newline='') as csvfile:
                    fieldnames = ['Title', 'Size', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
                    writer.writerow({'Title': '"'+str(productName)+'"', 'Size': '"'+str(productVariant)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
                    
            HCVID250_www_ediy_in_Spider.jsonData.append({'Title': productName, 'Size':productVariant, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
            
