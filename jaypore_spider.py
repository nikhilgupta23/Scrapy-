import scrapy
import csv
class JayporeSpider(scrapy.Spider):
    name = "jaypore"
    products_seen = []
    def start_requests(self):
        url = "https://www.jaypore.com/"
        yield scrapy.Request(url=url, callback=self.parse)
    def parse(self, response):
        x = response.css('li.nav-items')
        for columns in x:
            y = columns.css('section.topnav-column ul.topnav-menu-links')            
            for z in y:
                head_category = z.css('a h3::text').extract_first()
                list_items = z.css('li')
                for item in list_items:
                    page = item.css('a::attr(href)').extract_first()
                    sub_category = item.css('a::text').extract_first()
                    if page is not None:
                        request = scrapy.Request(url=page, callback = self.parsePage)
                        request.meta['category'] = str(head_category) + ' - ' + str(sub_category)
                        yield request
    def parsePage(self, response):        
        products = response.css('li.proditems')        
        for product in products:            
            product_link = product.css('a::attr(href)').extract_first()
            if product_link not in JayporeSpider.products_seen:
                JayporeSpider.products_seen.append([product_link])
                request = scrapy.Request(url=product_link, callback=self.parseProduct)
                request.meta['product_link'] = product_link
                request.meta['category'] = response.meta['category']                
                yield request
    def parseProduct(self, response):
        productLink = response.meta['product_link']
        productCategory = response.meta['category']
        productName = response.css('h1.productName::text').extract_first()
        productImage = response.css('div.lftPanel img::attr(src)').extract_first()
        productDesc = ''
        productDescUl = response.css('ul.prdDisc span#prodDesc li')
        for li in productDescUl:
            productDesc = productDesc + li.css('::text').extract_first() + '\n'
        productDesc = productDesc[:-1]
        productPrice = response.css('span#dPrice::text').extract_first()
        with open('jaypore.csv', 'a', newline='') as csvfile:
            fieldnames = ['Name', 'Image', 'Description', 'Price', 'Page', 'Category']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)            
            writer.writerow({'Name': productName, 'Image': productImage, 'Description': productDesc,'Price': productPrice, 'Page': productLink, 'Category': productCategory})        
            
