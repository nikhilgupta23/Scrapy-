import scrapy
from scrapy.selector import HtmlXPathSelector
import json

class QuotesSpider(scrapy.Spider):
    name = "final"
    def start_requests(self):
        for i in range (117):
            url="https://www.mojarto.com/artists?page=" + str(i+1)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        hxs = HtmlXPathSelector(response)
        arr1=[]
        hey=hxs.select('//div[@class="list-container listpadding"]/div[@class="collapse"]/div[@class="product-details"]//p/a/@href').extract()
        for i in hey:
            print (i)
            ok="https://www.mojarto.com" + i
            arr1.append(ok)
        print (len(arr1))
        for j in arr1:
            yield scrapy.Request(url=j, callback=self.parseProduct)
    def parseProduct(self,response):
        page = response.url.split("/")[-2]
        hxs = HtmlXPathSelector(response)
        item= hxs.select('//li[@class="white-panel artist-data"]/div[@class="browse-box"]/div[@class="browseinner"]/div[@class="product-details" or @class="product-price"]//text()').extract()
        c=0
        d=0
        img=hxs.select('//li[@class="white-panel artist-data"]/div[@class="browse-box"]/div[@class="browseimg"]/a/img/@src').extract()
        for i in img:
            d+=1
        print ('number of image urls is = ' + str(d) + '  in ' + response.url)
        arr=[]
        pro=''
        for i in item : 
            string=str(i)
            if (len(i)==1):
                continue;
            r=string.replace("\n" , '')
            if (r not in 'Added to cart'):
                pro+=r + '$'
            else :
                arr.append(pro)
                pro=''
        data={}
        d=0
        for i in arr:
            x=i.split('$')
            title=x[0]
            by=x[2]
            details =  'by ' + by + ' , ' + x[3] + '  ' + x[4]
            price = x[5]
            imgurl=img[d]
            if (d==0):
                data[by]=[]
            data[by].append({
            'name' : title,
            'description' : details,
            'price' : price,
            'imageUrl' : imgurl
            })
            d+=1
        with open('dataMojartoFinal.txt', 'a') as outfile:
            json.dump(data, outfile)

            
