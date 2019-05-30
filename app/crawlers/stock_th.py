import shutil
import time

import backtrader as bt
import pandas as pd
import requests

from datetime import datetime, timedelta
from lxml import etree

from app.common import date_utils, number_utils, storage_utils


class SETCrawler(object):
    NVDR_CELLS_PER_ROW = 11

    @classmethod
    def crawl_price(cls, symbols, fromdate, todate=None):
        assert isinstance(symbols, list), 'symbols must be list of string'
        assert isinstance(fromdate, datetime), 'fromdate must be datetime'
        assert todate is None or isinstance(todate, datetime), 'todate must be datetime or None'
        assert todate is None or fromdate <= todate, 'fromdate must be earlier than todate'

        fromdate = date_utils.strip_time(fromdate)
        todate = date_utils.strip_time(todate) if todate else fromdate

        for symbol in symbols:
            print(f'>> {symbol}')

            yahoo_symbol = f'{symbol}.BK'

            data = bt.feeds.YahooFinanceData(dataname=yahoo_symbol, fromdate=fromdate, todate=todate)
            data.start()

            with open(storage_utils.abs_path('SET/StockPrice/', f'{yahoo_symbol}.csv'), 'w') as fd:
                data.f.seek(0)
                shutil.copyfileobj(data.f, fd)

    @classmethod
    def crawl_nvdr(cls, fromdate, todate=None):
        """
        Crawl NVDR from set.or.th

        :param fromdate: Datetime format
        :param todate: Datetime format
        :return: List of List
        """

        assert isinstance(fromdate, datetime), 'fromdate must be datetime'
        assert todate is None or isinstance(todate, datetime), 'todate must be datetime or None'
        assert todate is None or fromdate <= todate, 'fromdate must be earlier than todate'

        fromdate = date_utils.strip_time(fromdate)
        todate = date_utils.strip_time(todate) if todate else fromdate

        crawl_date = fromdate
        while crawl_date <= todate:
            print(f'>> {crawl_date}')

            request_url = 'https://www.set.or.th/set/nvdrbystock.do?format=excel&date={}'.format(
                crawl_date.strftime('%d/%m/%Y'))
            response = requests.get(request_url)

            response_tree = etree.HTML(response.content)
            tds = response_tree.xpath('//table[2]/tr[position()>2]/td')

            data = []
            for x in range(0, len(tds), cls.NVDR_CELLS_PER_ROW):
                row = tds[x:x+cls.NVDR_CELLS_PER_ROW]
                data.append([
                    row[0].text,  # Symbol
                    number_utils.clean_num_string(row[1].text),  # Volume Buy
                    number_utils.clean_num_string(row[2].text),  # Volume Sell
                    number_utils.clean_num_string(row[6].text),  # Value Buy
                    number_utils.clean_num_string(row[7].text),  # Value Sell
                    number_utils.clean_num_string(row[5].text),  # Percentage
                ])

            if data:
                df = pd.DataFrame.from_records(
                    data, columns=['Symbol', 'Volume Buy', 'Volume Sell', 'Value Buy', 'Value Sell', 'Percentage'])
                df.to_csv(storage_utils.abs_path(
                    'SET/NVDR/', 'NVDR-{}.csv'.format(crawl_date.strftime('%Y-%m-%d'))), index=False)

            crawl_date = crawl_date + timedelta(days=1)
            time.sleep(2)
