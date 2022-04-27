import scrapy
import unidecode
import re
import logging

cleanString = lambda x: '' if x is None else unidecode.unidecode(re.sub(r'\s+',' ',x))


class ElpaisSpider(scrapy.Spider):
    name = 'elpais'
    allowed_domains = ['www.elpais.com']
    start_urls = ['https://elpais.com/']

    def parse(self, response):
        # logging.log(logging.WARNING, response.css("section").extract())
        sect = response.css("section")
        # logging.log(logging.WARNING, sect.attrib['class'])

        # for secttitle in response.css("section::attr(data-dtm-region)").extract():
        #     # sect_name = sect.attrib['class']
        #     # if "data-dtm-region" in sect.attrib:
            

        #     logging.log(logging.WARNING, secttitle)

        for s in sect:
            section_name = 'No section name'

            if 'data-dtm-region' in s.attrib:
                section_name = s.attrib['data-dtm-region']
            
            # logging.log(logging.WARNING, section_name)
            for article in s.css("article"):
                    title = article.css("a::text").extract_first()
                    url = response.url[:-1] + article.css("a::attr(href)").extract_first()
                    summary =  article.css("p::text").extract_first()
                    
                    if url.count('https') >= 2:
                        url = article.css("a::attr(href)").extract_first()
                    if summary == None: summary = "No summary"
                # yield{
                    # logging.log(logging.WARNING, title)
                    # logging.log(logging.WARNING, url)
                    # logging.log(logging.WARNING, p)
                # }
                    yield {
                    'section': section_name,
                    'appears_ulr': response.url,
                    'title': cleanString(title),
                    'article_url': url,
                    'summary': cleanString(summary),
                    }
        # logging.log(logging.WARNING, response.css(".c_t a::text").extract())

        
