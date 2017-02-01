import scrapy
import csv
import json
import re
from html.parser import HTMLParser
from scrapy.http import HtmlResponse

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

class HCVID172_www_sosgardenshop_com_Spider(scrapy.Spider):
    name = "HCVID172.www.sosgardenshop.com"
    products_seen = []
    jsonData = []

    def closed(self, reason):
        toWrite = {'data' : HCVID172_www_sosgardenshop_com_Spider.jsonData}
        with open('./json/HCVID172.www.sosgardenshop.com.json', 'w+') as outfile:    
            json.dump(toWrite, outfile, ensure_ascii=False)
    
    def start_requests(self):        
        page = 'http://www.sosgardenshop.com/Hanging-catid-967090-page-1.html'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Accessory|Hanging'
        yield request
        page = 'http://www.sosgardenshop.com/Table-Top-Planters-catid-339658-page-1.html'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Stoneware|Table Top Planters'
        yield request
        page = 'http://www.sosgardenshop.com/Wall-Planters-catid-339659-page-1.html'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Stoneware|Wall Planters'
        yield request
        page = 'http://www.sosgardenshop.com/Table-Top--catid-736146-page-1.html'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Collectables|Table Top'
        yield request
        page = 'http://www.sosgardenshop.com/Hanging-Table-top-catid-904130-page-1.html'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Collectables|Hanging/Table Top'
        yield request
        page = 'http://www.sosgardenshop.com/Wall-planters-catid-984569-page-1.html'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Glazed|Wall Planters'        
        yield request
        page = 'http://www.sosgardenshop.com/Hanging-catid-339672-page-1.html'
        request = scrapy.Request(url=page, callback = self.parsePage)        
        request.meta['category'] = 'Glazed|Hanging'        
        yield request

        headers = {'Cookie':'JSESSIONID=22DDB18F50A4DCFE08FDFE2AFEF94C2D; ext_name=jaehkpjddfdgiiefcnhahapilbejohhj', 'Content-Type':'application/json'}
        data = '{"page":"1","pageSize":"50","filters":{"F_subCategoryId":["339662"]}}'
        page = 'http://www.sosgardenshop.com/api/search.action?storeId=19270'
        request = scrapy.Request(url=page, headers=headers, body=data, callback = self.parsePage)        
        request.meta['category'] = 'Glazed|Table Top Planters'
        yield request
        

    def parsePage(self, response):
        if response.meta['category'] == 'Glazed|Table Top Planters':
            output = json.loads(response.body_as_unicode())
            for prod in output["products"]:
                productLink = 'http://www.sosgardenshop.com' + prod["productURL"]
                productCategory = response.meta['category']
                productImage = prod["productImages"][0]["productImageUrl"]["medium"]
                productName = prod["name"]
                productSku = prod["code"]
                productPrice = prod["retailPrice"]
                productDesc = prod["description"]

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

                with open('HCVID172.www.sosgardenshop.com.csv', 'a', newline='') as csvfile:
                    fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
                    writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})

                HCVID172_www_sosgardenshop_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})                    
        else:
            cat = response.meta['category']
            products = response.css('input[name="productsHtmlResult"]::attr(value)').extract_first()
            response = HtmlResponse(url="my HTML string", encoding='utf-8', body=products.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", "\"").replace("&gt;", ">").replace("&quot;", "\'").replace("&amp;", "&"))
            products = response.css('article#allProducts > section')
            for product in products:
                product_link = 'http://www.sosgardenshop.com' + product.css('a::attr(href)').extract_first()
                request = scrapy.Request(url=product_link, callback=self.parseProduct)
                request.meta['product_link'] = product_link
                request.meta['category'] = cat
                yield request
            
    def parseProduct(self, response):
        productLink = response.meta['product_link']
        productCategory = response.meta['category']
        productImage = response.css('div#gallery a::attr(href)').extract_first()
        productName = response.css('span.breakword::text').extract_first()

        productPrice = response.css('div#price-section p::text').extract_first().replace('Rs.','').strip()
        productDesc = response.css('div#l5_prodDesc').extract_first()
        if productDesc:
            productDesc = strip_tags(productDesc)
        
        productSku = response.css('p.txt12.m0::text').extract_first().replace('(SKU ID:','').replace(')','').strip()

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

        with open('HCVID172.www.sosgardenshop.com.csv', 'a', newline='') as csvfile:
            fieldnames = ['Title', 'Category', 'URL', 'IMG_SRC', 'Merchant', 'Price', 'SKU', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Title': '"'+str(productName)+'"', 'IMG_SRC': '"'+str(productImage)+'"', 'Description': '"'+str(productDesc)+'"','Price': '"'+str(productPrice)+'"', 'URL': '"'+str(productLink)+'"', 'Category': '"'+str(productCategory)+'"', 'SKU': '"'+str(productSku)+'"', 'Merchant': '"NA"'})

        HCVID172_www_sosgardenshop_com_Spider.jsonData.append({'Title': productName, 'Description': productDesc, 'IMG_SRC': productImage, 'Price': productPrice, 'SKU': productSku, 'Category': productCategory, 'URL': productLink, 'Merchant': 'NA'})
            
