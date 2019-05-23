# -*- coding: utf-8 -*-
import scrapy


class StockPrice(scrapy.Item):
    symbol = scrapy.Field()
    date = scrapy.Field()  # วันที่
    price_open = scrapy.Field()  # ราคาเปิด
    price_high = scrapy.Field()  # ราคาสูงสุด
    price_low = scrapy.Field()  # ราคาต่ำสุด
    price_avg = scrapy.Field()  # ราคาเฉลี่ย
    price_close = scrapy.Field()  # ราคาปิด
    trade_volume = scrapy.Field()  # ปริมาณ (พันหุ้น)
    trade_value = scrapy.Field()  # มูลค่า (ล้านบาท)

    CSV_FILENAME = 'SET-PRICE-{symbol}.csv'
    CSV_COLUMNS = ['symbol', 'date', 'price_open', 'price_high', 'price_low', 'price_avg', 'price_close', 'trade_volume', 'trade_value']
    CSV_UNIQUE_COLUMNS = ['symbol', 'date']


class StockNVDR(scrapy.Item):
    symbol = scrapy.Field()
    date = scrapy.Field()  # วันที่
    volume_buy = scrapy.Field()
    volume_sell = scrapy.Field()
    value_buy = scrapy.Field()
    value_sell = scrapy.Field()

    CSV_FILENAME = 'SET-NVDR-{symbol}.csv'
