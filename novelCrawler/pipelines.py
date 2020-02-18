# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import logging
import pymongo
from .items import ChapterItem, NovelCrawlerItem


class NovelCrawlerPipeline(object):
    novels_collection = 'novels'
    chapters_collection = 'chapters'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGODB_HOST'),
            mongo_db=crawler.settings.get('MONGODB_DATABASE', 'NovelBase')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, ChapterItem):
            # store chapter item into MongoDB
            self.db[self.chapters_collection].insert_one(dict(item))
            logging.info('chapter item: %d', item['index'])
        elif isinstance(item, NovelCrawlerItem):
            # store novel item into MongoDB
            self.db[self.novels_collection].insert_one(dict(item))
            logging.info('novel item: {}'.format(item['name']))
        return item
