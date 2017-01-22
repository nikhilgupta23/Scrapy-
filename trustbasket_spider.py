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

class HCVID285_trustbasket_com_Spider(scrapy.Spider):
    name = "HCVID285.trustbasket.com"
    products_seen = []
    jsonData = []

    def closed(self, reason):
        toWrite = {'data' : HCVID285_trustbasket_com_Spider.jsonData}
        with open('./json/HCVID285.trustbasket.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
    
    def start_requests(self):
        url = "http://www.trustbasket.com/"
        yield scrapy.Request(url=url, callback=self.parse)
        
    def parse(self, response):        
        x = response.css('ul#accessibleNav > li')
        for columns in x:
            head_category = columns.css('a::text').extract_first().strip()                
            if head_category != 'Home' and head_category != 'Composter' and head_category != 'Terracotta' and head_category != 'Plants' and head_category != 'More':
                list_items = columns.css('ul > li')
                for item in list_items:
                    page = item.css('a::attr(href)').extract_first()
                    sub_category = item.css('a::text').extract_first().strip()                            
                    if page is not None:
                        print(page)
                        request = scrapy.Request(url= 'http://www.trustbasket.com' + page + '?page=1', callback = self.parsePage)
                        request.meta['pagenum'] = 1
                        request.meta['category'] = str(head_category) + '|' + str(sub_category)
                        yield request
        page = 'http://www.trustbasket.com/pages/indoor-bokashi-composter'
        request = scrapy.Request(url=page+'?page=1', callback = self.parsePage)
        request.meta['pagenum'] = 1
        request.meta['category'] = 'Composter'
        yield request
        page = 'http://www.trustbasket.com/collections/terracotta-clay-planters-pots'
        request = scrapy.Request(url=page+'?page=1', callback = self.parsePage)
        request.meta['pagenum'] = 1
        request.meta['category'] = 'Terracotta'
        yield request
        page = 'http://www.trustbasket.com/collections/plants'
        request = scrapy.Request(url=page+'?page=1', callback = self.parsePage)
        request.meta['pagenum'] = 1
        request.meta['category'] = 'Plants'
        yield request        

    def parsePage(self, response):
        products = response.css('div.grid.grid-border div.grid-uniform > div.grid-item')
        print(len(products),response.request.url)
        if len(products) == 1 and 'Sorry' in products.css('p::text').extract_first().strip():
            return
        else:
            for product in products:
                product_link = 'http://www.trustbasket.com' + product.css('a::attr(href)').extract_first()
                product_name = product.css('p::text').extract_first()
                product_image = product.css('img::attr(src)').extract_first()
                request = scrapy.Request(url=product_link, callback=self.parseProduct)
                request.meta['product_link'] = product_link
                request.meta['product_image'] = product_image
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
        productName = response.meta['product_name']

        productPrice = response.css('meta[itemprop="price"]::attr(content)').extract_first().replace('Rs.','').strip()
        productDesc = response.css('div.product-description').extract_first()
        if productDesc:
            productDesc = strip_tags(productDesc)
        
        content = response.css('script[type=text\/javascript]').extract_first()
        data = json.loads(re.search('var meta = (.*?);', content).group(1))
        productSku = data["product"]["variants"][0]["sku"]

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

        with open('HCVID285.trustbasket.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})
            
        HCVID285_trustbasket_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
            
