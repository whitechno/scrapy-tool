"""
Run it:
> scrapy crawl bw-public -a region=US -a letterIn=1
"""
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy import log

import os

from tutorial.items import BwItem
from tutorial import settings

class DmozSpider(BaseSpider):
    name = "dmoz"
    allowed_domains = ["dmoz.org"]
    start_urls = [
        "http://www.dmoz.org/Computers/Programming/Languages/Python/Books/",
        "http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/"
    ]
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        sites = hxs.select('//ul/li')
        for site in sites:
            title = site.select('a/text()').extract()
            link = site.select('a/@href').extract()
            desc = site.select('text()').extract()
            print title, link, desc
            

class BwSpider(BaseSpider):
    name = "bw-public"
    allowed_domains = ["businessweek.com"]
    
    symbollookup_url = "http://investing.businessweek.com/research/common/symbollookup/symbollookup.asp?lookuptype=public"
    snapshot_url = "http://investing.businessweek.com/research/stocks/snapshot/snapshot.asp"
    snapshot_article_url = "http://investing.businessweek.com/research/stocks/snapshot/snapshot_article.asp"
    
    #region = "Americas"
    #letterIn = "Z"
    start_firstrow = "0"
    #start_urls = [symbollookup_url + "&region=" + region + "&letterIn=" + letterIn + "&firstrow=" + start_firstrow]
    
    def __init__(self, region=None, letterIn=None, *args, **kwargs):
        super(BwSpider, self).__init__(*args, **kwargs)
        
        ### region, letterIn, start_urls
        self.region = region
        self.letterIn = letterIn
        self.start_urls = [self.symbollookup_url +
                           "&region=" + self.region +
                           "&letterIn=" + self.letterIn + 
                           "&firstrow=" + self.start_firstrow]
    
        ### setting log file: LOG_ROOT/<spider name>/<region>/<letterIn>/<spider name>-<region>-<letterIn>.log
        log_path = os.path.join(settings.LOG_ROOT, self.name, self.region, self.letterIn)
        if not os.path.isdir(log_path):
            os.makedirs(log_path)
        log_file = os.path.join(log_path, '-'.join([self.name, self.region, self.letterIn]) + '.log')
        if os.path.isfile(log_file):
            os.remove(log_file)
        print "log file: ", log_file
        log.start(logfile=log_file, loglevel=log.INFO, logstdout=False)
        
        ### setting json data output: DATA_ROOT/<spider name>/<region>/<letterIn>/<spider name>-<region>-<letterIn>.json
        data_path = os.path.join(settings.DATA_ROOT, self.name, self.region, self.letterIn)
        if not os.path.isdir(data_path):
            os.makedirs(data_path)
        data_file = os.path.join(data_path, '-'.join([self.name, self.region, self.letterIn]) + '.json')
        if os.path.isfile(data_file):
            os.remove(data_file)
        print "data file: ", data_file
        self.data_file = data_file
        
        
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        #items = []
        requests = []
        
        ### for record-keeping purposes what lookup page are we on?
        lookup_page = ''.join(hxs.select('//span[@class="onLink"]/text()').extract())
        
        rows = hxs.select('//div[@id="columnLeft"]/table/tbody/tr')
        log.msg("!!!!! page: " + lookup_page + " | rows: " + str(len(rows)), level = log.INFO if len(rows) > 0 else log.WARNING)
        
        ### process lookup results table
        lookup_row = 0
        for row in rows:
            lookup_row += 1
            item = BwItem()
            item['lookup_page'] = lookup_page
            item['lookup_row'] = str(lookup_row)
            item['region'] = self.region
            item['letter_in'] = self.letterIn
            
            columns = row.select('td')
            try:
                item['name'] = columns[0].select('a/text()').extract()[0]
                item['ticker'] = columns[0].select('a/@href').re('ticker=(.+)')[0]
                item['country'] = columns[1].select('text()').extract()[0]
                item['capital_iq_industry'] = columns[2].select('text()').extract()[0]
                #print name, '\t', ticker, '\t', country, '\t', capital_iq_industry, '\n\n'
                
                request = Request(url=self.snapshot_url + "?ticker=" + item['ticker'],
                                  callback=self.parse_snapshot)
                request.meta['item'] = item
                requests.append(request)
                #items.append(item)
            except:
                log.msg("\n++++++++++++++++++++++++++++++\n" + 
                        "lookup selector failed for page: " + item['lookup_page'] + ", row: " + item['lookup_row'] + "\n" + 
                        response.url + "\n\n",
                        level=log.WARNING)
        
        ### go to the next lookup results page
        next_firstrow = ''.join(hxs.select('//a[@class="nextBtnActive"]/@href').re('firstrow=(\d+)'))
        log.msg("!!!!! next_firstrow: |" + next_firstrow + "|", level=log.INFO)
        if next_firstrow != '':
            request = Request(url=self.symbollookup_url + \
                              "&region=" + self.region + \
                              "&letterIn=" + self.letterIn + \
                              "&firstrow=" + next_firstrow,
                              callback=self.parse)
            requests.append(request)
        
        return requests

    def parse_snapshot(self, response):
        item = response.meta['item']
        item['snapshot_url'] = response.url
        
        hxs = HtmlXPathSelector(response)
        
        try:
            ### sector & industry
            item['sector'] = ''.join(hxs.select('//a[@class="link_xs bold sector"]/text()').re('(.+) SECTOR$'))
            item['industry'] = ''.join(hxs.select('//a[@class="link_xs bold sector"]/text()').re('(.+) INDUSTRY$'))
            item['sector_code'] = ''.join(hxs.select('//a[@class="link_xs bold sector"]/@href').re('sectordetail.asp\?code=(\d+)'))
            item['industry_code'] = ''.join(hxs.select('//a[@class="link_xs bold sector"]/@href').re('industrydetail.asp\?code=(\d+)'))
            
            ### stock exchange
            item['exchange'] = ''.join(hxs.select('//h2[@class="pageHeader"]/span/text()').extract()[2])
            
            ### detailsContainer
            item['web_url'] = ''.join(hxs.select('//div[@class="detailsDataContainerLt"]/div[@itemprop="url"]/a/@href').extract())
            item['web_txt'] = ''.join(hxs.select('//div[@class="detailsDataContainerLt"]/div[@itemprop="url"]/a/text()').extract())
            
            item['employees_num'] = ''.join(hxs.select('//div[@class="detailsDataContainerLt"]/div/strong/text()').extract())
            item['employees_date'] = ''.join(hxs.select('//div[@class="detailsDataContainerLt"]/div/span/text()').re('Last Reported Date:\s+(.+)'))
            
            item['year_founded'] = ''.join(hxs.select('//div[@class="detailsDataContainerLt"]/div/strong/span[@itemprop="foundingDate"]/text()').extract())
            
            item['description_short'] = ''.join(hxs.select('//div[@itemprop="description"]/p/text()').extract())
        except:
            log.msg("\n++++++++++++++++++++++++++++++\n" + 
                    "snapshot selector failed for " + item['ticker'] + " " + item['name'] + "\n" + 
                    response.url + "\n\n",
                    level=log.WARNING)
        
        ### go to snapshot article
        request = Request(url=self.snapshot_article_url + "?ticker=" + item['ticker'],
                                       callback=self.parse_snapshot_article)
        request.meta['item'] = item
        return request

    def parse_snapshot_article(self, response):
        item = response.meta['item']
        item['snapshot_article_url'] = response.url
        
        hxs = HtmlXPathSelector(response)
        try:
            item['hq_address'] = ' | '.join(hxs.select('//div[@itemprop="address"]/p/text()').extract())
            item['phone'] = ''.join(hxs.select('//span[@itemprop="telephone"]/text()').extract())
        except:
            log.msg("\n++++++++++++++++++++++++++++++\n" + 
                    "snapshot_article selector failed for " + item['ticker'] + " " + item['name'] + "\n" + 
                    response.url + "\n\n",
                    level=log.WARNING)
            
        return item
    
    