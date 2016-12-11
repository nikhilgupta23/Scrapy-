import scrapy
import csv
import urllib
from urllib.parse import urlparse
class AsianPaintsSpider(scrapy.Spider):
    name = "asian_paints"
    products_seen = []

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
            print('\n',item_link,'\n')
            request = scrapy.Request(url=item_link, callback=self.parseProduct)
            print(response.meta['category'])
            request.meta['category'] = response.meta['category']
            request.meta['prod_link'] = item_link
            yield request
            
    def parseProduct(self, response):
        productLink = response.meta['prod_link']
        productCategory = response.meta['category']        
        productDesc = response.css('div#tab-1::text').extract_first()
        productDesc = str(productDesc).strip()
        if not productDesc:
            print("hola")
            productDesc = str(response.css('div#tab-1 p::text').extract_first())
            productDesc = productDesc.strip()
        productName = response.css('h1.color_dark.fw_medium::text').extract_first()        
        productImage = response.css('img#zoom_image::attr(src)').extract_first()        
        productPrice = response.css('span.v_align_b.m_left_5.scheme_color.fw_medium::text').extract_first()
        with open('asianPaints.csv', 'a', newline='') as csvfile:
            fieldnames = ['Name', 'Image', 'Description', 'Category', 'Price', 'Page']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Name': productName, 'Image': productImage, 'Description': productDesc,'Price': productPrice, 'Page': productLink, 'Category': productCategory})
            
