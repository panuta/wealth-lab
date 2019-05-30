import datetime

from django.core.management.base import BaseCommand

from app.crawlers.stock_th import SETCrawler


class Command(BaseCommand):
    help = 'Crawl data'

    def handle(self, *args, **options):
        fromdate = datetime.datetime(2017, 1, 1)
        todate = datetime.datetime(2019, 5, 24)

        # SETCrawler.crawl_price(symbols=[], fromdate=fromdate, todate=todate)
        SETCrawler.crawl_nvdr(fromdate=fromdate, todate=todate)
