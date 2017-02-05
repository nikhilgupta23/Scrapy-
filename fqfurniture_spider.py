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

class HCVID315_www_fqfurniture_com_Spider(scrapy.Spider):
    name = "HCVID315.www.fqfurniture.com"
    products_seen = []
    jsonData = []

    def closed(self, reason):
        toWrite = {'data' : HCVID315_www_fqfurniture_com_Spider.jsonData}
        with open('./json/HCVID315.www.fqfurniture.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
    
    def start_requests(self):
        url = "https://fqfurniture.com/"
        yield scrapy.Request(url=url, callback=self.parse)
        
    def parse(self, response):
        scripts = response.css('script::text').extract()
        data = None
        for script in scripts:
            if 'baconMenu.menus =' in script:
                data = json.loads(re.search('baconMenu.menus = (.*?);', script).group(1))
                break
        print(data)
        for header in data:
            head_category = header["handle"]
            if head_category != 'sale':
                for x in header["sub_items"]["items"]:
                    for child in x["sub_items"]:
                        page = 'https://fqfurniture.com' + child["path"]
                        sub_category = child["display_title"]                            
                        request = scrapy.Request(url= page + '?page=1', callback = self.parsePage)
                        request.meta['pagenum'] = 1                    
                        request.meta['category'] = str(head_category) + '|' + str(sub_category)
                        yield request
##        x = response.css('ul#menu > li')        
##        for columns in x:
##            head_category = columns.css('a::text').extract_first().strip()
##            if head_category != 'SALE':
##                list_items = columns.css('div.bacon-street.normal ul li')
##                for item in list_items:
##                    page = 'https://fqfurniture.com/' + item.css('a::attr(href)').extract_first()
##                    sub_category = item.css('a::text').extract_first().strip()                            
##                    if page is not None:                    
##                        request = scrapy.Request(url= page + '?p=1', callback = self.parsePage)
##                        request.meta['pagenum'] = 1
##                        request.meta['category'] = str(head_category) + '|' + str(sub_category)
##                        yield request

    def parsePage(self, response):
        products = response.css('div.products div.one-third')
        if not products:
            return
        for product in products:
            product_link = 'https://fqfurniture.com' + product.css('a::attr(href)').extract_first()
            product_image = product.css('div.product_image img::attr(src)').extract_first()
            product_price = product.css('meta[itemprop="price"]::attr(content)').extract_first()
            product_name = product.css('span[itemprop="name"]::text').extract_first()
            request = scrapy.Request(url=product_link, callback=self.parseProduct)
            request.meta['product_link'] = product_link
            request.meta['product_image'] = product_image
            request.meta['product_price'] = product_price
            request.meta['product_name'] = product_name
            request.meta['product_category'] = response.meta['category']
            yield request
        nextpage = response.meta['pagenum'] + 1
        product_link = response.request.url[:response.request.url.index('?page=')] + '?page=' + str(nextpage)
        request = scrapy.Request(url=product_link, callback=self.parsePage)
        request.meta['category'] = response.meta['category']
        request.meta['pagenum'] = nextpage
        yield request

    def parseProduct(self, response):
        productLink = response.meta['product_link']
        productCategory = response.meta['product_category']
        productImage = response.meta['product_image']        
        productPrice = response.meta['product_price']
        productName = response.meta['product_name']
        
        productDesc = response.css('div.fd-product-tab-content > div').extract_first()
        if not productDesc:
            productDesc = 'NA'
        else:
            productDesc = strip_tags(productDesc)
            
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

        with open('HCVID315.www.fqfurniture.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
        
        HCVID315_www_fqfurniture_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
            
