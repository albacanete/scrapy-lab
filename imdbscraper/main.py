from scrapy import cmdline

cmdline.execute("scrapy crawl imdb -o imdb2.json".split())