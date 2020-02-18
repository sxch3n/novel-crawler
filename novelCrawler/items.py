# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

# project items definition file

import scrapy


class NovelCrawlerItem(scrapy.Item):
    No = scrapy.Field()
    name = scrapy.Field()
    author = scrapy.Field()
    status = scrapy.Field()
    link = scrapy.Field()
    chapter_urls = scrapy.Field()
    chapter_titles =scrapy.Field()


class ChapterItem(scrapy.Item):
    novel_no = scrapy.Field()
    index = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    link = scrapy.Field()
