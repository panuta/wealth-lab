# -*- coding: utf-8 -*-
import scrapy
from dateutil.parser import parse


class KaohoonSpider(scrapy.Spider):
    name = 'kaohoon'

    def start_requests(self):
        yield scrapy.Request('https://www.kaohoon.com/content/tag/foreign-investors', self.parse_list)

    def parse_list(self, response):
        for article_id in response.xpath('//article/@id').getall():
            article_id = article_id.split('-')[1]
            yield scrapy.Request(response.urljoin('/content/{article_id}'.format(
                article_id=article_id)), self.parse_article)
            break

    def parse_article(self, response):
        excerpt = response.xpath('//p[@class="entry-excerpt"]/text()').getall()[0]
        _, _, date_text = excerpt.rpartition('on')
        article_date = parse(date_text)

        tables = response.xpath('//article/descendant::table')
        symbols_for_top_purchased_by_value = self._symbols_from_table(tables[2])
        symbols_for_top_sold_by_value = self._symbols_from_table(tables[3])

    def _symbols_from_table(self, table):
        return [table_row.xpath('.//td/text()').getall() for table_row in table.xpath('.//tr')[1:]]
