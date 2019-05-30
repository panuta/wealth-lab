import datetime
import os
import shutil

import backtrader as bt
import pandas as pd

from pathlib import Path
from django.core.management.base import BaseCommand

STORAGE_ROOT = './storage/'


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        # parser.add_argument('spider', nargs='+', type=int)
        parser.add_argument('symbols', default='')

    def handle(self, *args, **options):
        symbols = options['symbols'].split(',')

        fromdate = datetime.datetime(2017, 1, 1)
        todate = datetime.datetime(2019, 5, 24)

        os.mkdir(Path('{}{}'.format(STORAGE_ROOT, 'SET/StockPrice/')).resolve())

        for symbol in symbols:
            print(f'>> {symbol}')

            yahoo_symbol = f'{symbol}.BK'

            data = bt.feeds.YahooFinanceData(dataname=yahoo_symbol, fromdate=fromdate, todate=todate)
            data.start()

            filename = f'{yahoo_symbol}.csv'
            csv_file_abspath = Path('{}{}{}'.format(STORAGE_ROOT, 'SET/', filename)).resolve()
            with open(csv_file_abspath, 'w') as fd:
                data.f.seek(0)
                shutil.copyfileobj(data.f, fd)

            symbol_df = pd.read_csv(csv_file_abspath).set_index(keys=['Date'])



