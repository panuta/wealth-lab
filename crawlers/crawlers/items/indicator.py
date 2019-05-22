# -*- coding: utf-8 -*-
import scrapy


class Indicator(scrapy.Item):
    date = scrapy.Field()
    symbol = scrapy.Field()
    indicator_name = scrapy.Field()
    indicator_type = scrapy.Field()
    values = scrapy.Field()

    # MongoDB
    UNIQUE_KEYS = ['symbol', 'date', 'indicator_name', 'indicator_type']
