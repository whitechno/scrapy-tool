"""
Run it:
> scrapy crawl bw-private -a region=US -a letterIn=1
"""
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy import log

import os

from tutorial.items import BwItem
from tutorial import settings

class BwPrivateSpider(BaseSpider):
    name = "bw-private"
    allowed_domains = ["businessweek.com"]
    
    symbollookup_url = "http://investing.businessweek.com/research/common/symbollookup/symbollookup.asp?lookuptype=private"
    snapshot_url = "http://investing.businessweek.com/research/stocks/private/snapshot.asp"
    
    start_firstrow = "0"
    
    def __init__(self, region=None, letterIn=None, *args, **kwargs):
        super(BwPrivateSpider, self).__init__(*args, **kwargs)
        
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
            #print columns
            try:
                item['name'] = columns[0].select('a/text()').extract()[0]
                item['ticker'] = columns[0].select('a/@href').re('privcapid=(.+)')[0]
                item['country'] = columns[1].select('text()').extract()[0]
                item['capital_iq_industry'] = columns[2].select('text()').extract()[0]
                
                #print item
                request = Request(url=self.snapshot_url + "?privcapid=" + item['ticker'],
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
            
            item['sector'] = ''.join(hxs.select('//h3[@class="txtC6 floatL"]/text()').extract())
            
            ### detailsContainer
            
            item['hq_address'] = ' | '.join(hxs.select('//div[@itemprop="address"]/p/text()').extract())
            
            item['year_founded'] = ''.join(hxs.select('//div[@class="detailsDataContainerLt"]/div/p/strong/span[@itemprop="foundingDate"]/text()').extract())
            
            item['phone'] = ''.join(hxs.select('//p[@itemprop="telephone"]/text()').extract())
        
            item['web_url'] = ''.join(hxs.select('//div[@class="detailsDataContainerRt"]/div/p/a[@itemprop="url"]/@href').extract())
            item['web_txt'] = ''.join(hxs.select('//div[@class="detailsDataContainerRt"]/div/p/a[@itemprop="url"]/text()').extract())
            
            #item['description_short'] = ''.join(hxs.select('//p[@itemprop="description"]/text()').extract())
            item['description_short'] = ''.join(hxs.select('//p[@id="bDesc"]/text()').extract())
        
            #print item
        except:
            log.msg("\n++++++++++++++++++++++++++++++\n" + 
                    "snapshot selector failed for " + item['ticker'] + " " + item['name'] + "\n" + 
                    response.url + "\n\n",
                    level=log.WARNING)
            
        
        return item
    