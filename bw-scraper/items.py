# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class DmozItem(Item):
    # define the fields for your item here like:
    # name = Field()
    title = Field()
    link = Field()
    desc = Field()

class BwItem(Item):
    
    ### logs, errors
    lookup_page = Field() # NN  ##PRIVATE
    lookup_row = Field() # NN   ##PRIVATE
    #selector_fail = Field()
    
    ### top
    region = Field() # NN       ##PRIVATE
    letter_in = Field() # NN    ##PRIVATE
    
    ### symbollookup
    name = Field() # NN U       ##PRIVATE
    ticker = Field() # NN U     ##PRIVATE
    country = Field() # NN      ##PRIVATE
    capital_iq_industry = Field() # NN  ##PRIVATE
    
    ### snapshot
    snapshot_url = Field()      ##PRIVATE
    sector = Field()            ##PRIVATE
    sector_code = Field()
    industry = Field()
    industry_code = Field()
    exchange = Field() # NN
    web_url = Field()           ##PRIVATE
    web_txt = Field()           ##PRIVATE
    employees_num = Field()
    employees_date = Field()
    year_founded = Field()      ##PRIVATE
    description_short = Field() ##PRIVATE
    
    ### snapshot article
    snapshot_article_url = Field()
    hq_address = Field()        ##PRIVATE
    phone = Field()             ##PRIVATE
    description_long = Field()

