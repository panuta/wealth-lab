from decimal import Decimal

import pymongo
from bson import Decimal128


class MongoDBPipeline(object):
    collection_name = 'items'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        collection_name = getattr(spider, 'collection_name', None)
        if collection_name:
            self.collection_name = collection_name

        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

        unique_indexes = getattr(spider, 'unique_indexes', None)
        if unique_indexes:
            self.db[self.collection_name].create_index(unique_indexes, unique=True)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        item_dict = dict(item)
        for key, value in item_dict.items():
            if isinstance(value, Decimal):
                item_dict[key] = Decimal128(value)

        unique_keys = getattr(item, 'UNIQUE_KEYS', None)

        if not unique_keys:
            self.db[self.collection_name].insert_one(item_dict)
        else:
            query = {key: item_dict[key] for key in unique_keys}
            self.db[self.collection_name].update_one(query, {'$set': item_dict}, upsert=True)

        return item
