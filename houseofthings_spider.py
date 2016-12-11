import scrapy
import csv
import urllib
from urllib.parse import urlparse
class HouseOfThingsSpider(scrapy.Spider):
    name = "house_of_things"
    products_seen = []
    start_urls = [
        'http://www.thehouseofthings.com/mod/shop/x-shop.inc.php?xAction=getProducts&offSet=1&shortedBy=P.dateAdded%20DESC&catIDs=2',
        'http://www.thehouseofthings.com/mod/shop/x-shop.inc.php?xAction=getProducts&offSet=1&shortedBy=P.dateAdded%20DESC&catIDs=3',
        'http://www.thehouseofthings.com/mod/shop/x-shop.inc.php?xAction=getProducts&offSet=1&shortedBy=P.dateAdded%20DESC&catIDs=4',
        'http://www.thehouseofthings.com/mod/shop/x-shop.inc.php?xAction=getProducts&offSet=1&shortedBy=P.dateAdded%20DESC&catIDs=5',
        'http://www.thehouseofthings.com/mod/shop/x-shop.inc.php?xAction=getProducts&offSet=1&shortedBy=P.dateAdded%20DESC&catIDs=6',
        'http://www.thehouseofthings.com/mod/shop/x-shop.inc.php?xAction=getProducts&offSet=1&shortedBy=P.dateAdded%20DESC&catIDs=7',
        'http://www.thehouseofthings.com/mod/shop/x-shop.inc.php?xAction=getProducts&offSet=1&shortedBy=P.dateAdded%20DESC&catIDs=8',
        'http://www.thehouseofthings.com/mod/shop/x-shop.inc.php?xAction=getProducts&offSet=1&shortedBy=P.dateAdded%20DESC&catIDs=10',
        'http://www.thehouseofthings.com/mod/shop/x-shop.inc.php?xAction=getProducts&offSet=1&shortedBy=P.dateAdded%20DESC&catIDs=11',
        'http://www.thehouseofthings.com/mod/shop/x-shop.inc.php?xAction=getProducts&offSet=1&shortedBy=P.dateAdded%20DESC&catIDs=12',
        'http://www.thehouseofthings.com/mod/shop/x-shop.inc.php?xAction=getProducts&offSet=1&shortedBy=P.dateAdded%20DESC&catIDs=13',
        'http://www.thehouseofthings.com/mod/shop/x-shop.inc.php?xAction=getProducts&offSet=1&shortedBy=P.dateAdded%20DESC&catIDs=16',
        'http://www.thehouseofthings.com/mod/shop/x-shop.inc.php?xAction=getProducts&offSet=1&shortedBy=P.dateAdded%20DESC&catIDs=17'
        ]
        
    def parse(self, response):
        items = response.css('li')
        source = response.request.url

        parsed = urlparse(source)
        qs = urllib.parse.parse_qs(parsed.query)
        id1 = int(qs['catIDs'][0])

        print(id1,'\n\n')
        category = ''
        if id1 == 2:
            category = 'Objet D\' Art'
        elif id1 == 3:
            category = 'Wall Art'
        elif id1 == 4:
            category = 'Sculpture'
        elif id1 == 5:
            category = 'Furniture'                
        elif id1 == 6:
            category = 'Jewellery'                
        elif id1 == 7:
            category = 'Textiles'                
        elif id1 == 8:
            category = 'Tableware'                
        elif id1 == 10:
            category = 'Lighting'                
        elif id1 == 11:
            category = 'Home Accents'                
        elif id1 == 12:
            category = 'Timepieces'                
        elif id1 == 13:
            category = 'Games'                
        elif id1 == 16:
            category = 'Junior'                
        elif id1 == 17:
           category = 'Stationery'
        for item in items:
            prod_link = item.css('a::attr(href)').extract_first()
            image_link = item.css('img::attr(src)').extract_first()
            request = scrapy.Request(url=prod_link, callback = self.parseProduct)          
            request.meta['prod_link'] = prod_link                
            request.meta['category'] = category
            request.meta['image_link'] = image_link
            yield request
            
    def parseProduct(self, response):
        productLink = response.meta['prod_link']
        productCategory = response.meta['category']
        productBrand = response.css('div.product-details h3 a::text').extract_first()
        productDesc = response.css('p.fb-desc::text').extract_first()
        productDesc = str(productDesc).strip()
        productName = response.css('h1::text').extract_first()        
        productImage = response.meta['image_link']
        productPrice = response.css('span.price::text').extract_first() if response.css('span.price::text').extract_first() != None else 'Price On Request'
        with open('houseOfThings.csv', 'a', newline='') as csvfile:
            fieldnames = ['Name', 'Image', 'Brand', 'Description', 'Category', 'Price', 'Page']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Name': productName, 'Image': productImage, 'Description': productDesc,'Price': productPrice, 'Page': productLink, 'Category': productCategory, 'Brand': productBrand})
            
