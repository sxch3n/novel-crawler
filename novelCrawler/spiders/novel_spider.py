import re
import pymongo
import scrapy
from novelCrawler.items import NovelCrawlerItem, ChapterItem


class NovelSpider(scrapy.Spider):
    name = "novel"

    def start_requests(self):
        # put novel pages urls here
        urls = [
            "https://www.biquge.com.cn/book/35922/",
            "https://www.biquge.com.cn/book/33556/",
            "https://www.biquge.com.cn/book/29105/",
            "https://www.biquge.com.cn/book/39923/"
        ]
        for url in urls:
            yield scrapy.Request(url=url, dont_filter=True, callback=self.parse, meta={'index': 0})

    def parse(self, response):
        chapter_urls = response.css('div#list dd a::attr(href)').getall()
        chapters_set = set(chapter_urls)
        # check existence of the novel and scrape only new chapters
        client = pymongo.MongoClient(self.settings.get('MONGODB_HOST'))
        db = client[str(self.settings.get('MONGODB_DATABASE'))]
        book_no = response.request.url.split("/")[-2]
        novel = db['novels'].find_one_and_delete({'No': book_no})
        client.close()
        if novel:
            old_chapters = set(novel.get('chapter_urls'))
            chapters = chapters_set - old_chapters
        else:
            chapters = chapter_urls
        item = NovelCrawlerItem()
        item['No'] = book_no
        item['link'] = response.request.url
        # TODO: change to generic url - should be able to get url from whatever link provided
        base_url = "https://www.biquge.com.cn"
        item['name'] = response.css('div#info h1::text').get()
        author = response.css('div#info p::text')[0].extract()
        status = response.css('div#info p::text')[1].extract()
        item['status'] = re.findall(r"(.+)：(.+[^,])", status)[0][1]
        item['author'] = re.findall(r"(.+)：(.+)", author)[0][1]
        item['chapter_urls'] = chapter_urls
        item['chapter_titles'] = response.css('div#list dd a::text').getall()
        yield item

        for idx, url in enumerate(chapter_urls):
            if url in chapters:
                cplt_url = base_url + url
                yield scrapy.Request(url=cplt_url, dont_filter=True, callback=self.parse_content,
                                     meta={'index': idx + 1, 'No': item['No']})

    def parse_content(self, response):
        # set chapter item
        item = ChapterItem()
        item['novel_no'] = response.meta['No']
        item['link'] = response.request.url
        item['index'] = response.meta['index']
        item['title'] = response.xpath('//h1/text()').get()
        item['content'] = response.xpath("//div[@id='content'][1]/text()").getall()
        return item
