import scrapy
import unidecode
import re
import logging

cleanString = lambda x: '' if x is None else unidecode.unidecode(re.sub(r'\s+',' ',x))

class ImdbSpider(scrapy.Spider):
    name = 'imdb'
    allowed_domains = ['www.imdb.com']
    start_urls = ['https://www.imdb.com/title/tt0096463/fullcredits/']

    def parse(self, response):

        # We have pairs of actor and role in this table list which we will specify next
        cast = response.css(".cast_list")
        

        # classes odd and even contain the list of all of the actors and their roles
        actorsInfo = cast.css(".odd, .even")

        actors_roles =[]

        # We extrat the actors name from the photo's title, the role from the text labeled
        # as character, and the id from the photo's link. We didn't directly get the name 
        # the table because that text isn't well labeled, and we found it quite hard to get
        # this information otherwise since it only has td as label, nothing else.

        for i in range(0, len(actorsInfo.css(".character a::text").extract())):
            actor = cleanString(actorsInfo.css(".primary_photo img::attr(title)").extract()[i])
            id = actorsInfo.css(".primary_photo a::attr(href)").extract()[i].split('/')[2]
            role = cleanString(actorsInfo.css(".character a::text").extract()[i])
            actors_roles.append((actor, role, id))

        # Then we just grab all of the information about the movie
        movie_id = response.url.split('/')[-3]
        movie_name =  response.css(".subnav_heading::text").extract_first()
        movie_year =  response.css("span[class=nobr]::text").extract_first().strip()[1:-1]

        for actor in actors_roles:
            yield {   
                
                "movie_id": movie_id, 
                "movie_name": movie_name, 
                "movie_year": movie_year,
                "actor_name": actor[0], 
                "actor_id": actor[1], 
                "role_name": actor[2]
            }
