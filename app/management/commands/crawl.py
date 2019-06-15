from datetime import datetime

from django.core.management.base import BaseCommand

from app.crawlers.thai_stock_crawler import ThaiStockCrawler


class Command(BaseCommand):
    help = 'Crawl latest data'

    def handle(self, *args, **options):
        fromdate = datetime(2017, 1, 1)

        print('Load symbols')
        symbols = ThaiStockCrawler.load_symbols(crawl_if_not_exists=True)

        print('Crawl price')
        ThaiStockCrawler.crawl_price(symbols=symbols, fromdate=fromdate)

        print('Crawl NVDR')
        ThaiStockCrawler.crawl_nvdr(fromdate=fromdate)
