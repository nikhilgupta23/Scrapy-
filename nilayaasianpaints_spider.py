import scrapy
import csv
import urllib
import re
import json
from urllib.parse import urlparse
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

class HCVID242_nilaya_asianpaints_com_Spider(scrapy.Spider):
    name = "HCVID242.nilaya.asianpaints.com"
    products_seen = []
    jsonData = []

    def closed(self, reason):
        toWrite = {'data' : HCVID242_nilaya_asianpaints_com_Spider.jsonData}
        with open('./json/HCVID242.nilaya.asianpaints.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)

    def start_requests(self):
        for x in range(8):
            url = 'http://nilaya.asianpaints.com/wall-decor-online/bytype/wall-stickers?commerce_price_amount=All&sort_by=title&sort_order=ASC&items_per_page=15&page=' + str(x)            
            request = scrapy.Request(url=url, callback=self.parse)
            request.meta['category'] = 'Wall-Stickers'        
            yield request
        for z in range(5):
            url = 'http://nilaya.asianpaints.com/wall-decor-online/bytype/borders?commerce_price_amount=All&sort_by=title&sort_order=ASC&items_per_page=15&page=' + str(z)
            request = scrapy.Request(url=url, callback=self.parse)
            request.meta['category'] = 'Borders'        
            yield request
        for y in range(34):
            url = 'http://nilaya.asianpaints.com/designer-wallpapers?commerce_price_amount=All&sort_by=title&sort_order=ASC&items_per_page=60&page=' + str(y)
            request = scrapy.Request(url=url, callback=self.parse)
            request.meta['category'] = 'Wallpapers'        
            yield request


        url = 'http://nilaya.asianpaints.com/featuredcollection/sea-escape-by-nilaya'
        request = scrapy.Request(url=url, callback=self.parse)
        request.meta['category'] = 'Signatures - Sea Escape'        
        yield request

        url = 'http://nilaya.asianpaints.com/featuredcollection/moods-of-monsoon-by-nilaya'
        request = scrapy.Request(url=url, callback=self.parse)
        request.meta['category'] = 'Signatures - Moods of Monsoon'        
        yield request
        
        url = 'http://nilaya.asianpaints.com/featuredcollection/charbagh'
        request = scrapy.Request(url=url, callback=self.parse)
        request.meta['category'] = 'Good Earth for Nilaya - Charbagh'        
        yield request


        url = 'http://nilaya.asianpaints.com/featuredcollection/palmyra'
        request = scrapy.Request(url=url, callback=self.parse)
        request.meta['category'] = 'Good Earth for Nilaya - Palmyra'        
        yield request

        url = 'http://nilaya.asianpaints.com/featuredcollection/xanadu'
        request = scrapy.Request(url=url, callback=self.parse)
        request.meta['category'] = 'Good Earth for Nilaya - Xanadu'        
        yield request

        url = 'http://nilaya.asianpaints.com/featuredcollection/xanadu'
        request = scrapy.Request(url=url, callback=self.parse)
        request.meta['category'] = 'Good Earth for Nilaya - Xanadu'        
        yield request


        url = 'http://nilaya.asianpaints.com/featuredcollection/spice-route'
        request = scrapy.Request(url=url, callback=self.parse)
        request.meta['category'] = 'Sabyasachi for Nilaya - Spice Route'        
        yield request

        url = 'http://nilaya.asianpaints.com/featuredcollection/varanasi'
        request = scrapy.Request(url=url, callback=self.parse)
        request.meta['category'] = 'Sabyasachi for Nilaya - Varanasi'        
        yield request

        url = 'http://nilaya.asianpaints.com/featuredcollection/jodhpur'
        request = scrapy.Request(url=url, callback=self.parse)
        request.meta['category'] = 'Sabyasachi for Nilaya - Jodhpur'        
        yield request

        url = 'http://nilaya.asianpaints.com/featuredcollection/india-baroque'
        request = scrapy.Request(url=url, callback=self.parse)
        request.meta['category'] = 'Sabyasachi for Nilaya - India Baroque'        
        yield request

        url = 'http://nilaya.asianpaints.com/featuredcollection/makhmal'
        request = scrapy.Request(url=url, callback=self.parse)
        request.meta['category'] = 'Sabyasachi for Nilaya - Makhmal'        
        yield request
        
            
    def parse(self, response):
        items = response.css('a.d_block.relative')
        for item in items:            
            item_link = 'http://nilaya.asianpaints.com'+ str(item.css('::attr(href)').extract_first())
            request = scrapy.Request(url=item_link, callback=self.parseProduct)
            request.meta['category'] = response.meta['category']
            request.meta['prod_link'] = item_link
            yield request
            
    def parseProduct(self, response):
        productLink = response.meta['prod_link']
        productCategory = response.meta['category']        
        productDesc = response.css('div#tab-1').extract_first()        
        if productDesc:
            productDesc = strip_tags(productDesc)
        productName = response.css('h1.color_dark.fw_medium::text').extract_first()        
        productImage = response.css('img#zoom_image::attr(src)').extract_first()        
        productPrice = response.css('span.v_align_b.m_left_5.scheme_color.fw_medium::text').extract_first()
        productSku = response.css('div.t_xs_align_l.col-lg-6.col-md-6.col-sm-12.col-xs-12 div.m_bottom_10::text').extract_first()

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

        with open('HCVID242.nilaya.asianpaints.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})

        HCVID242_nilaya_asianpaints_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
            
