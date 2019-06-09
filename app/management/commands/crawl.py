from datetime import datetime

from django.core.management.base import BaseCommand

from app.crawlers.set_crawler import SETCrawler


class Command(BaseCommand):
    help = 'Crawl latest data'

    def handle(self, *args, **options):
        fromdate = datetime(2017, 1, 1)

        print('Load symbols')
        symbols = SETCrawler.load_symbols(crawl_if_not_exists=True)

        print('Crawl price')
        SETCrawler.crawl_price(symbols=symbols, fromdate=fromdate)

        print('Crawl NVDR')
        SETCrawler.crawl_nvdr(fromdate=fromdate)
