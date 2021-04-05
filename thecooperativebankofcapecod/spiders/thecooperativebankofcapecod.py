import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from thecooperativebankofcapecod.items import Article


class thecooperativebankofcapecodSpider(scrapy.Spider):
    name = 'thecooperativebankofcapecod'
    start_urls = ['https://www.thecooperativebankofcapecod.com/about/news/']

    def parse(self, response):
        links = response.xpath('//a[@class="_self pt-cv-readmore btn btn-success"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//ul[@class="pt-cv-pagination pt-cv-ajax pagination"]/li[last()]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="entry-meta"]/text()').get()
        if date:
            date = " ".join(date.split()[2:])

        content = response.xpath('//div[@class="entry-content"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
