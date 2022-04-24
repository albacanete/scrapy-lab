import scrapy
import unidecode
import re
import logging

cleanString = lambda x: '' if x is None else unidecode.unidecode(re.sub(r'\s+',' ',x))

class NytimesSpider(scrapy.Spider):
    name = 'nytimes'
    allowed_domains = ['www.nytimes.com']
    start_urls = ['https://www.nytimes.com/']

    def parse(self, response):
        count = 0
        logging.log(logging.WARNING, "response" + str(response.css("section story-wrapper")))
        logging.log(logging.WARNING, "type" + str(type(response)))


        # logging.log(logging.WARNING, str(response.css("section").get()))
        for section in response.css("section"):
            logging.log(logging.WARNING, "type2" + str(type(section)))
            logging.log(logging.WARNING, "count " + str(count) + ' ' + str(section))
            logging.log(logging.WARNING, str(type(section.css('h3::text'))))
            logging.log(logging.WARNING, section.css('h3::text').extract_first())
            logging.log(logging.WARNING, section.css('a h3::text, a h3 span::text').extract_first())

            logging.log(logging.WARNING, str(len(section.xpath('//h3['+str(count)+']//text()').getall())))
            # logging.log(logging.WARNING, response.url)
            # logging.log(logging.WARNING, 'attrib is:')
            # logging.log(logging.WARNING, section.css)

            # logging.log(logging.WARNING, str(type(section.xpath('//h1['+str(count)+']//text()').get())))

            count+=1
            # section_name = section.attrib['data-block-tracking-id']
            # for article in section.css("section"):
            #     yield {
            #         'section': section_name,
            #         'appears_ulr': response.url,
            #         'title': cleanString(article.css('a h3::text, a h3 span::text').extract_first()),
            #         'article_url': response.url[:-1]+article.css('a::attr(href)').extract_first(),
            #         'summary': cleanString(''.join(article.css('p::text, ul li::text').extract())),
                # }