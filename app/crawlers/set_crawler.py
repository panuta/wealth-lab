import requests
import shutil
import time

from datetime import datetime, timedelta
from lxml import etree
from pathlib import Path

from app.common import date_utils, number_utils, storage_utils, string_utils


class SETCrawler(object):
    NVDR_CELLS_PER_ROW = 11

    SYMBOLS_FILE_PATH_TUPLE = ('SET/', 'symbols.txt')

    @classmethod
    def crawl_symbols(cls):
        response = requests.get('https://www.set.or.th/dat/eod/listedcompany/static/listedCompanies_th_TH.xls')
        encoded_content = response.content.decode('iso-8859-11').encode('utf-8')
        response_tree = etree.HTML(encoded_content)

        symbols = []
        for symbol_tr in response_tree.xpath('//table[1]/tr[position()>2]'):
            market = symbol_tr.xpath('td[3]')[0].text.strip()
            if market == 'SET':
                symbols.append(symbol_tr.xpath('td[1]')[0].text.strip())

        with open(storage_utils.abs_path(*cls.SYMBOLS_FILE_PATH_TUPLE), 'w') as fd:
            fd.write('\n'.join(symbols))

    @classmethod
    def load_symbols(cls, crawl_if_not_exists=False):
        symbols_filepath = storage_utils.abs_path(*cls.SYMBOLS_FILE_PATH_TUPLE)
        symbols_file = Path(symbols_filepath)
        if not symbols_file.is_file():
            if crawl_if_not_exists:
                cls.crawl_symbols()
            else:
                return None

        with open(symbols_filepath, 'r') as fd:
            symbols = fd.read().splitlines()
        return symbols

    @classmethod
    def crawl_price(cls, symbols, fromdate, todate=None):
        if not todate:
            todate = datetime.today()
        todate = date_utils.strip_time(todate)
        fromdate = date_utils.strip_time(fromdate)

        import backtrader as bt
        for symbol in symbols:
            yahoo_symbol = f'{string_utils.encode_symbol_for_yahoo_finance(symbol)}.BK'
            data = bt.feeds.YahooFinanceData(dataname=yahoo_symbol, fromdate=fromdate, todate=todate)
            data.start()

            with open(storage_utils.abs_path('SET/Price/', f'{yahoo_symbol}.csv'), 'w') as fd:
                data.f.seek(0)
                shutil.copyfileobj(data.f, fd)

    @classmethod
    def crawl_nvdr(cls, fromdate, todate=None):
        if not todate:
            todate = datetime.today()
        todate = date_utils.strip_time(todate)
        fromdate = date_utils.strip_time(fromdate)

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
                import pandas as pd
                df = pd.DataFrame.from_records(
                    data, columns=['Symbol', 'Volume Buy', 'Volume Sell', 'Value Buy', 'Value Sell', 'Percentage'])
                df.to_csv(storage_utils.abs_path(
                    'SET/NVDR/', 'NVDR-{}.csv'.format(crawl_date.strftime('%Y-%m-%d'))), index=False)

            crawl_date = crawl_date + timedelta(days=1)
            time.sleep(2)
