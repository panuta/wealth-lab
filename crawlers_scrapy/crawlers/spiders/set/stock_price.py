# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime

from crawlers.items.set_market import StockPrice
from crawlers.utils import str_to_numeric


class SETTradeStockPriceSpider(scrapy.Spider):
    name = 'set_stock_price'

    def __init__(self, symbols=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if symbols:
            self.symbol_list = symbols.split(',')
        else:
            self.symbol_list = []

    def start_requests(self):
        for symbol in self.symbol_list:
            request_url = 'https://www.settrade.com/' \
                          'C04_02_stock_historical_p1.jsp?' \
                          'txtSymbol={}&selectPage=2&max=200&offset=0'.format(symbol.upper())
            yield scrapy.Request(request_url, self.parse, meta={'symbol': symbol})

    def parse(self, response):
        tables = response.xpath('//div[@id="maincontent"]/descendant::table')

        if not tables:
            self.logger.error('Parse Error: Cannot find price table')
            return

        price_table = tables[0]

        for table_row in price_table.xpath('.//tbody/tr'):
            values = table_row.xpath('.//td/text()').getall()

            if len(values) != 12:
                self.logger.warn('Parse Error: Table schema might changed')
                continue

            yield StockPrice(
                symbol=response.meta['symbol'],
                date=datetime.strptime(values[0], '%d/%m/%y').strftime('%Y-%m-%d'),
                price_open=str_to_numeric(values[1]),
                price_high=str_to_numeric(values[2]),
                price_low=str_to_numeric(values[3]),
                price_avg=str_to_numeric(values[4]),
                price_close=str_to_numeric(values[5]),
                trade_volume=str_to_numeric(values[8]),
                trade_value=str_to_numeric(values[9]),
            )
