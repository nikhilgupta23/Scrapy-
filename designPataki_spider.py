import scrapy
import csv
import json

class DesignPatakiSpider(scrapy.Spider):
    name = "design_pataki"
    jsonData = []
    start_urls = [
            'http://shop.designpataki.com/monogram.html?limit=all',
            'http://shop.designpataki.com/kids.html?limit=all',
            'http://shop.designpataki.com/trousseau.html?limit=all',
            'http://shop.designpataki.com/homedecor.html?limit=all',
            'http://shop.designpataki.com/stationary.html?limit=all',
            'http://shop.designpataki.com/tableware-2.html?limit=all'
        ]
        
    def parse(self, response):        
        source = response.request.url
        category = ''
        if "monogram" in source:
            category = "Monogram Store"
        elif "kids" in source:
            category = "Kids"
        elif "trousseau" in source:
            category = "Bridal"
        elif "homedecor" in source:
            category = "Home Decor"
        elif "stationary" in source:
            category = "Stationary"
        elif "tableware" in source:
            category = "Tableware"

        items = response.css('li.hklist.item')    
        for item in items:            
            prod_link = item.css('a::attr(href)').extract_first()
            image_link = item.css('img::attr(src)').extract_first()
            request = scrapy.Request(url=prod_link, callback = self.parseProduct)
            request.meta['prod_link'] = prod_link                
            request.meta['category'] = category
            request.meta['image_link'] = image_link
            yield request

    def closed(self, reason):
        with open('data.json', 'w+') as outfile:    
            json.dump(DesignPatakiSpider.jsonData, outfile)

        
    def parseProduct(self, response):        
        productLink = response.meta['prod_link']
        productCategory = response.meta['category']        
        parts = response.css('div#accordion div::text').extract()
        productDesc = ''
        for part in parts:            
            productDesc += part
        productDesc = productDesc.strip()
        productName = response.css('div.product-name h1::text').extract_first()        
        productImage = response.meta['image_link']
        productPrice = str(response.css('span.regular-price span.price::text').extract_first()).replace('INR','').strip()

        productCategory = productCategory.replace('"','``')
        productDesc = productDesc.replace('"','``')
        productName = productName.replace('"','``')
        productSku = 'SKU-NA'
        
        with open('designPataki.csv', 'a', newline='') as csvfile:
            fieldnames = ['Name', 'Image', 'Description', 'Category', 'Price', 'Page', 'SKU']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Name': '"'+productName+'"', 'Image': '"'+productImage+'"', 'Description': '"'+productDesc+'"','Price': '"'+productPrice+'"', 'Page': '"'+productLink+'"', 'Category': '"'+productCategory+'"', 'SKU': '"'+productSku+'"'})

        DesignPatakiSpider.jsonData.append({'Name': productName, 'Image': productImage, 'Description': productDesc,'Price': productPrice, 'Page': productLink, 'Category': productCategory, 'SKU': productSku})        
