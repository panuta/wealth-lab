from datetime import datetime

from django.core.management.base import BaseCommand

from app.common import date_utils
from app.crawlers.set_crawler import SETCrawler


class Command(BaseCommand):
    help = 'Crawl latest data'

    def handle(self, *args, **options):
        fromdate = datetime(2017, 1, 1)

        symbols = SETCrawler.load_symbols(crawl_if_not_exists=True)
        SETCrawler.crawl_price(symbols=symbols, fromdate=fromdate)

        SETCrawler.crawl_nvdr(fromdate=fromdate)


        # SETCrawler.crawl_price(symbols=[], fromdate=fromdate, todate=todate)
        # SETCrawler.crawl_nvdr(fromdate=fromdate, todate=todate)
