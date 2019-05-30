import datetime

from django.core.management.base import BaseCommand

from app.crawlers.stock_th import SETCrawler

STORAGE_ROOT = './storage/'


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        fromdate = datetime.datetime(2019, 5, 24)
        # todate = datetime.datetime(2019, 5, 24)

        SETCrawler.crawl_nvdr(datetime.datetime(2019, 5, 24))
