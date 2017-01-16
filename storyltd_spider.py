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

class HCVID175_www_storyltd_com_Spider(scrapy.Spider):
    name = "HCVID175.www.storyltd.com"
    products_seen = []
    jsonData = []

    def closed(self, reason):
        toWrite = {'data' : HCVID175_www_storyltd_com_Spider.jsonData}
        with open('./json/HCVID175.www.storyltd.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
    
    def start_requests(self):
        url = "https://www.storyltd.com/"
        yield scrapy.Request(url=url, callback=self.parse)
        
    def parse(self, response):        
        x = response.css('div#top_navigation_navigationListHolder ul#top_navigation_top_menus_list > li')        
        for columns in x:
            head_category = columns.css('a::text').extract_first()
            if head_category != 'Artists' and head_category != 'Auctions':
                list_items = columns.css('div.block1:first-child ul li')                
                for item in list_items:
                    page = item.css('a::attr(href)').extract_first()
                    sub_category = item.css('a::text').extract_first()                            
                    if page is not None:
                        print(page)
                        request = scrapy.Request(url=page, callback = self.parsePage)
                        request.meta['category'] = str(head_category) + '|' + str(sub_category)
                        yield request
                        
    def parsePage(self, response):
        scripts = response.css('script[type=text\/javascript]').extract()
        for script in scripts:
            if 'var urlBase' in script and 'var pageIndex' in script:
                link = 'https://www.storyltd.com' + re.search('var urlBase = \'(.*?)\';', script).group(1) + '&pageSize=60&pageIndex=1'
                request = scrapy.Request(url=link, callback=self.parseOthers)
                request.meta['category'] = response.meta['category']
                request.meta['pagenum'] = 1
                yield request        

    def parseOthers(self, response):
        products = response.css('body > li')
        if not products:
            return
        else:
            for product in products:            
                product_link = product.css('a::attr(href)').extract_first()
                product_image = product.css('a img::attr(data-original)').extract_first()
                request = scrapy.Request(url=product_link, callback=self.parseProduct)
                request.meta['product_link'] = product_link
                request.meta['product_image'] = product_image
                request.meta['product_category'] = response.meta['category']
                yield request
            nextpage = response.meta['pagenum'] + 1
            product_link = response.request.url[:response.request.url.index('&pageIndex')] + '&pageIndex=' + str(nextpage)
            request = scrapy.Request(url=product_link, callback=self.parseOthers)
            request.meta['category'] = response.meta['category']
            request.meta['pagenum'] = nextpage
            yield request
                
    def parseProduct(self, response):
        productLink = response.meta['product_link']
        productCategory = response.meta['product_category']
        productImage = response.meta['product_image']        
        productMerchant = 'NA'
        productPrice = response.css('li#ContentPlaceHolder1_primary_price::text').extract_first().replace('Rs','').strip()
        
        productName = response.css('div.author-details h1::text').extract_first()
        if productName:
            productName += ' by ' 
            productName += response.css('div.author-details h2::text').extract_first()
        else:
            productName = response.css('div.author-details h2::text').extract_first()

        productDesc = response.css('div#ContentPlaceHolder1_itemdetails').extract_first()
        if not productDesc:
            productDesc = 'NA'
        else:
            productDesc = strip_tags(productDesc)

        productSku = ''
        texts = response.css('div#ContentPlaceHolder1_itemdetails::text').extract()
        for text in texts:
            if 'StoryLTD Ref No:' in text:
                productSku = text.replace('StoryLTD Ref No:','').strip()
        if not productSku:
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

        with open('HCVID175.www.storyltd.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"'+str(productMerchant)+'"'})

        HCVID175_www_storyltd_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': productMerchant})
            
