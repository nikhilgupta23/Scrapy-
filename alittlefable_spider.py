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

class HCVID291_www_alittlefable_com_Spider(scrapy.Spider):
    name = "HCVID291.www.alittlefable.com"
    jsonData = []
    start_urls = [
            'http://www.alittlefable.com/entity/ms.products?facetgroup=default_category_facet&facets=true&fields=%7B%22images%22:1,%22publish%22:1,%22name%22:1,%22alias%22:1,%22price%22:1,%22compare_price%22:1,%22available%22:1,%22list_price%22:1,%22our_price%22:1,%22original_price%22:1,%22options%22:1,%22attributes%22:1%7D&limit=1&q=%7B%22categories%22:%22baby%22,%22publish%22:%221%22%7D&sort=&start=0&total=1',
            'http://www.alittlefable.com/entity/ms.products?facetgroup=default_category_facet&facets=true&fields=%7B%22images%22:1,%22publish%22:1,%22name%22:1,%22alias%22:1,%22price%22:1,%22compare_price%22:1,%22available%22:1,%22list_price%22:1,%22our_price%22:1,%22original_price%22:1,%22options%22:1,%22attributes%22:1%7D&limit=1&q=%7B%22categories%22:%22boys%22,%22publish%22:%221%22%7D&sort=&start=0&total=1',
            'http://www.alittlefable.com/entity/ms.products?facetgroup=default_category_facet&facets=true&fields=%7B%22images%22:1,%22publish%22:1,%22name%22:1,%22alias%22:1,%22price%22:1,%22compare_price%22:1,%22available%22:1,%22list_price%22:1,%22our_price%22:1,%22original_price%22:1,%22options%22:1,%22attributes%22:1%7D&limit=1&q=%7B%22categories%22:%22girls%22,%22publish%22:%221%22%7D&sort=&start=0&total=1',
            'http://www.alittlefable.com/entity/ms.products?facetgroup=default_category_facet&facets=true&fields=%7B%22images%22:1,%22publish%22:1,%22name%22:1,%22alias%22:1,%22price%22:1,%22compare_price%22:1,%22available%22:1,%22list_price%22:1,%22our_price%22:1,%22original_price%22:1,%22options%22:1,%22attributes%22:1%7D&limit=1&q=%7B%22categories%22:%22women%22,%22publish%22:%221%22%7D&sort=&start=0&total=1',
            'http://www.alittlefable.com/entity/ms.products?facetgroup=default_category_facet&facets=true&fields=%7B%22images%22:1,%22publish%22:1,%22name%22:1,%22alias%22:1,%22price%22:1,%22compare_price%22:1,%22available%22:1,%22list_price%22:1,%22our_price%22:1,%22original_price%22:1,%22options%22:1,%22attributes%22:1%7D&limit=1&q=%7B%22categories%22:%22furniture%22,%22publish%22:%221%22%7D&sort=&start=0&total=1',
            'http://www.alittlefable.com/entity/ms.products?facetgroup=default_category_facet&facets=true&fields=%7B%22images%22:1,%22publish%22:1,%22name%22:1,%22alias%22:1,%22price%22:1,%22compare_price%22:1,%22available%22:1,%22list_price%22:1,%22our_price%22:1,%22original_price%22:1,%22options%22:1,%22attributes%22:1%7D&limit=1&q=%7B%22categories%22:%22footwear%22,%22publish%22:%221%22%7D&sort=&start=0&total=1',
            'http://www.alittlefable.com/entity/ms.products?facetgroup=default_category_facet&facets=true&fields=%7B%22images%22:1,%22publish%22:1,%22name%22:1,%22alias%22:1,%22price%22:1,%22compare_price%22:1,%22available%22:1,%22list_price%22:1,%22our_price%22:1,%22original_price%22:1,%22options%22:1,%22attributes%22:1%7D&limit=1&q=%7B%22categories%22:%22gifts%22,%22publish%22:%221%22%7D&sort=&start=0&total=1',
            'http://www.alittlefable.com/entity/ms.products?facetgroup=default_category_facet&facets=true&fields=%7B%22images%22:1,%22publish%22:1,%22name%22:1,%22alias%22:1,%22price%22:1,%22compare_price%22:1,%22available%22:1,%22list_price%22:1,%22our_price%22:1,%22original_price%22:1,%22options%22:1,%22attributes%22:1%7D&limit=1&q=%7B%22categories%22:%22accessories%22,%22publish%22:%221%22%7D&sort=&start=0&total=1',
            'http://www.alittlefable.com/entity/ms.products?facetgroup=default_category_facet&facets=true&fields=%7B%22images%22:1,%22publish%22:1,%22name%22:1,%22alias%22:1,%22price%22:1,%22compare_price%22:1,%22available%22:1,%22list_price%22:1,%22our_price%22:1,%22original_price%22:1,%22options%22:1,%22attributes%22:1%7D&limit=1&q=%7B%22categories%22:%22decor%22,%22publish%22:%221%22%7D&sort=&start=0&total=1'
        ]
        
    def parse(self, response):        
        source = response.request.url
        output = json.loads(response.body_as_unicode())
        
        link= ''
        if "baby" in source:
            link = 'http://www.alittlefable.com/entity/ms.products?facetgroup=default_category_facet&facets=true&fields=%7B%22images%22:1,%22publish%22:1,%22name%22:1,%22alias%22:1,%22price%22:1,%22compare_price%22:1,%22available%22:1,%22list_price%22:1,%22our_price%22:1,%22original_price%22:1,%22options%22:1,%22description%22:1,%22brand%22:1,%22attributes%22:1%7D&limit='+str(output["total"])+'&q=%7B%22categories%22:%22baby%22,%22publish%22:%221%22%7D&sort=&start=0&total=1'
        elif "boys" in source:
            link = 'http://www.alittlefable.com/entity/ms.products?facetgroup=default_category_facet&facets=true&fields=%7B%22images%22:1,%22publish%22:1,%22name%22:1,%22alias%22:1,%22price%22:1,%22compare_price%22:1,%22available%22:1,%22list_price%22:1,%22our_price%22:1,%22original_price%22:1,%22options%22:1,%22description%22:1,%22brand%22:1,%22attributes%22:1%7D&limit='+str(output["total"])+'&q=%7B%22categories%22:%22boys%22,%22publish%22:%221%22%7D&sort=&start=0&total=1'
        elif "girls" in source:
            link = 'http://www.alittlefable.com/entity/ms.products?facetgroup=default_category_facet&facets=true&fields=%7B%22images%22:1,%22publish%22:1,%22name%22:1,%22alias%22:1,%22price%22:1,%22compare_price%22:1,%22available%22:1,%22list_price%22:1,%22our_price%22:1,%22original_price%22:1,%22options%22:1,%22description%22:1,%22brand%22:1,%22attributes%22:1%7D&limit='+str(output["total"])+'&q=%7B%22categories%22:%22girls%22,%22publish%22:%221%22%7D&sort=&start=0&total=1'
        elif "women" in source:
            link = 'http://www.alittlefable.com/entity/ms.products?facetgroup=default_category_facet&facets=true&fields=%7B%22images%22:1,%22publish%22:1,%22name%22:1,%22alias%22:1,%22price%22:1,%22compare_price%22:1,%22available%22:1,%22list_price%22:1,%22our_price%22:1,%22original_price%22:1,%22options%22:1,%22description%22:1,%22brand%22:1,%22attributes%22:1%7D&limit='+str(output["total"])+'&q=%7B%22categories%22:%22women%22,%22publish%22:%221%22%7D&sort=&start=0&total=1'
        elif "furniture" in source:
            link = 'http://www.alittlefable.com/entity/ms.products?facetgroup=default_category_facet&facets=true&fields=%7B%22images%22:1,%22publish%22:1,%22name%22:1,%22alias%22:1,%22price%22:1,%22compare_price%22:1,%22available%22:1,%22list_price%22:1,%22our_price%22:1,%22original_price%22:1,%22options%22:1,%22description%22:1,%22brand%22:1,%22attributes%22:1%7D&limit='+str(output["total"])+'&q=%7B%22categories%22:%22furniture%22,%22publish%22:%221%22%7D&sort=&start=0&total=1'
        elif "footwear" in source:
            link = 'http://www.alittlefable.com/entity/ms.products?facetgroup=default_category_facet&facets=true&fields=%7B%22images%22:1,%22publish%22:1,%22name%22:1,%22alias%22:1,%22price%22:1,%22compare_price%22:1,%22available%22:1,%22list_price%22:1,%22our_price%22:1,%22original_price%22:1,%22options%22:1,%22description%22:1,%22brand%22:1,%22attributes%22:1%7D&limit='+str(output["total"])+'&q=%7B%22categories%22:%22footwear%22,%22publish%22:%221%22%7D&sort=&start=0&total=1'
        elif "gifts" in source:
            link = 'http://www.alittlefable.com/entity/ms.products?facetgroup=default_category_facet&facets=true&fields=%7B%22images%22:1,%22publish%22:1,%22name%22:1,%22alias%22:1,%22price%22:1,%22compare_price%22:1,%22available%22:1,%22list_price%22:1,%22our_price%22:1,%22original_price%22:1,%22options%22:1,%22description%22:1,%22brand%22:1,%22attributes%22:1%7D&limit='+str(output["total"])+'&q=%7B%22categories%22:%22gifts%22,%22publish%22:%221%22%7D&sort=&start=0&total=1'
        elif "accessories" in source:
            link = 'http://www.alittlefable.com/entity/ms.products?facetgroup=default_category_facet&facets=true&fields=%7B%22images%22:1,%22publish%22:1,%22name%22:1,%22alias%22:1,%22price%22:1,%22compare_price%22:1,%22available%22:1,%22list_price%22:1,%22our_price%22:1,%22original_price%22:1,%22options%22:1,%22description%22:1,%22brand%22:1,%22attributes%22:1%7D&limit='+str(output["total"])+'&q=%7B%22categories%22:%22accessories%22,%22publish%22:%221%22%7D&sort=&start=0&total=1'
        elif "decor" in source:
            link = 'http://www.alittlefable.com/entity/ms.products?facetgroup=default_category_facet&facets=true&fields=%7B%22images%22:1,%22publish%22:1,%22name%22:1,%22alias%22:1,%22price%22:1,%22compare_price%22:1,%22available%22:1,%22list_price%22:1,%22our_price%22:1,%22original_price%22:1,%22options%22:1,%22description%22:1,%22brand%22:1,%22attributes%22:1%7D&limit='+str(output["total"])+'&q=%7B%22categories%22:%22decor%22,%22publish%22:%221%22%7D&sort=&start=0&total=1'
        yield scrapy.Request(url=link, callback = self.parseCategory)
            
    def parseCategory(self,response):
        source = response.request.url
        output = json.loads(response.body_as_unicode())
        category = ''
        if "baby" in source:
            category = "Baby"
        elif "boys" in source:
            category = "Boys"
        elif "girls" in source:
            category = "Girls"
        elif "women" in source:
            category = "Women"
        elif "furniture" in source:
            category = "Furniture"
        elif "footwear" in source:
            category = "Footwear"
        elif "gifts" in source:
            category = "Gifts"
        elif "accessories" in source:
            category = "Accessories"
        elif "decor" in source:
            category = "Decor"

        for record in output["records"]:
            
            productLink = 'http://www.alittlefable.com/product/'+record["alias"]
            print('\n',record.keys(),productLink,'\n')
            productCategory = category
            try:
                productDesc = record["description"]
            except KeyError:
                productDesc = 'NA'
            if not productDesc:
                productDesc = 'NA'
            productName = record["name"]
            try:
                productImage = 'http://cdn.storehippo.com/s/57becbc1c7c3f63b45b0728e/'+record["images"][0]["image"]
            except KeyError:
                productImage = 'NA'
            try:
                productMerchant = record["brand"]
            except KeyError:
                productDesc = 'NA'
            productPrice = str(record["price"])
            productSku = 'SKU-NA'
            
            productCategory = productCategory.replace('"','``')

            productDesc = productDesc.replace('"','``')
            productDesc = strip_tags(productDesc)
            productDesc = re.sub('\n' ,'|',productDesc)
            productDesc = re.sub('\t','',productDesc)                             
            productDesc = re.sub('\r','',productDesc)
            productDesc = re.sub('[ ]+',' ',productDesc)
            productDesc = re.sub('(\| )+','|',productDesc)
            productDesc = re.sub('\|+','|',productDesc)
            
            productName = productName.replace('"','``')

            productDesc = remove_non_ascii(productDesc)        
            productCategory = remove_non_ascii(productCategory)                
            productName = remove_non_ascii(productName)
            
            with open('HCVID291.www.alittlefable.com.csv', 'a', newline='') as csvfile:
                fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
                writer.writerow({'Title': '"'+productName+'"', 'IMG_SRC': '"'+productImage+'"', 'Description': '"'+productDesc+'"','Price': '"'+productPrice+'"', 'URL': '"'+productLink+'"', 'Category': '"'+productCategory+'"', 'SKU': '"'+productSku+'"', 'Merchant': '"'+productMerchant+'"'})
            
            HCVID291_www_alittlefable_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})

            
    def closed(self, reason):
        toWrite = {'data' : HCVID291_www_alittlefable_com_Spider.jsonData}
        with open('HCVID291.www.alittlefable.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)

