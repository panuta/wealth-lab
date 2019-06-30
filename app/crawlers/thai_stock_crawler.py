import backtrader as bt
import pandas as pd
import requests
import shutil
import time

from datetime import datetime, timedelta
from lxml import etree
from pathlib import Path

from app.common import date_utils, number_utils, storage_utils, string_utils


class ThaiStockCrawler(object):

    # Symbols
    SYMBOLS_STORAGE_FOLDER = 'SET/'
    SYMBOLS_STORAGE_FILENAME = 'symbols.txt'

    # Price
    STOCK_PRICE_FOLDER = 'SET/Price/'

    # NVDR
    NVDR_STORAGE_FOLDER = 'SET/NVDR/'
    MERGED_NVDR_STORAGE_FOLDER = 'SET/NVDR/Merged/'

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

        with open(storage_utils.abs_path(cls.SYMBOLS_STORAGE_FOLDER, cls.SYMBOLS_STORAGE_FILENAME), 'w') as fd:
            fd.write('\n'.join(symbols))

    @classmethod
    def load_symbols(cls, crawl_if_not_exists=False):
        symbols_filepath = storage_utils.abs_path(cls.SYMBOLS_STORAGE_FOLDER, cls.SYMBOLS_STORAGE_FILENAME)
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

        for symbol in symbols:
            yahoo_symbol = f'{string_utils.encode_symbol_for_yahoo_finance(symbol)}.BK'
            data = bt.feeds.YahooFinanceData(dataname=yahoo_symbol, fromdate=fromdate, todate=todate)

            try:
                data.start()
            except FileNotFoundError:
                pass
            else:
                with open(storage_utils.abs_path(cls.STOCK_PRICE_FOLDER, f'{yahoo_symbol}.csv'), 'w') as fd:
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
            request_url = 'https://www.set.or.th/set/nvdrbystock.do?format=excel&date={}'.format(
                crawl_date.strftime('%d/%m/%Y'))
            response = requests.get(request_url)

            response_tree = etree.HTML(response.content)
            tds = response_tree.xpath('//table[2]/tr[position()>2]/td')

            data = []
            for x in range(0, len(tds), 11):  # 11 => cells per row
                row = tds[x:x+11]
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
                    cls.NVDR_STORAGE_FOLDER, 'NVDR-{}.csv'.format(crawl_date.strftime('%Y-%m-%d'))), index=False)

            crawl_date = crawl_date + timedelta(days=1)
            time.sleep(2)

    @classmethod
    def merge_nvdr(cls):
        data_frames = []
        for nvdr_filename in storage_utils.list_files(storage_utils.abs_path(cls.NVDR_STORAGE_FOLDER)):
            nvdr_date = datetime.strptime(nvdr_filename.partition('.')[0].partition('-')[2], '%Y-%m-%d')
            data_frames.append(pd.read_csv(storage_utils.abs_path(cls.NVDR_STORAGE_FOLDER, nvdr_filename)).assign(Date=lambda x: nvdr_date))

        combined_df = pd.concat(data_frames, sort=False)

        symbols = cls.load_symbols()

        for symbol in symbols:
            new_df = combined_df[combined_df['Symbol'] == symbol].sort_values(by=['Date'])
            new_df.to_csv(storage_utils.abs_path('{}Merged/'.format(cls.NVDR_STORAGE_FOLDER), '{}.csv'.format(symbol)), index=False)
