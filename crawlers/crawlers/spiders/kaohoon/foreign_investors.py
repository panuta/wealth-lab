# -*- coding: utf-8 -*-
import scrapy
from dateutil.parser import parse

from crawlers.items.indicator import Indicator
from crawlers.utils import str_to_numeric


class KaohoonForeignInvestorsSpider(scrapy.Spider):
    name = 'kaohoon_foreign_investors'
    indicator_name = 'kaohoon_foreign_investors'

    PAGES = 2  # Each page has 10 articles

    # MongoDB
    collection_name = 'kaohoon_foreign'
    unique_indexes = [('symbol', 1), ('date', 1)]

    def start_requests(self):
        for page in range(1, self.PAGES + 1):
            yield scrapy.Request('https://www.kaohoon.com/content/tag/foreign-investors{}'.format(
                '/page/{}'.format(page) if page > 1 else ''
            ), self.parse_list)

    def parse_list(self, response):
        for article_id in response.xpath('//article/@id').getall():
            article_id = article_id.split('-')[1]
            yield scrapy.Request(response.urljoin('/content/{article_id}'.format(
                article_id=article_id)), self.parse_article)

    def parse_article(self, response):
        excerpt = response.xpath('//p[@class="entry-excerpt"]/text()').getall()[0]
        _, _, date_text = excerpt.rpartition('on')
        article_date = parse(date_text)

        tables = response.xpath('//article/descendant::table')

        for indicator in self._generate_indicator_item(article_date, 'purchased', self._symbols_from_table(tables[2])):
            yield indicator

        for indicator in self._generate_indicator_item(article_date, 'sold', self._symbols_from_table(tables[3])):
            yield indicator

    def _symbols_from_table(self, table):
        return [table_row.xpath('.//td/text()').getall() for table_row in table.xpath('.//tr')[1:]]

    def _generate_indicator_item(self, article_date, indicator_type, table_values):
        indicators = []
        for (symbol, buy, sell, total, net) in table_values:
            indicators.append(Indicator(
                date=article_date,
                symbol=symbol,
                indicator_name=self.indicator_name,
                indicator_type=indicator_type,
                values={
                    'buy': str_to_numeric(buy),
                    'sell': str_to_numeric(sell),
                    'total': str_to_numeric(total),
                    'net': str_to_numeric(net)
                }
            ))
        return indicators