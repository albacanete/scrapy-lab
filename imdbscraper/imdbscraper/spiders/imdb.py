import scrapy
import unidecode
import re
import logging

cleanString = lambda x: '' if x is None else unidecode.unidecode(re.sub(r'\s+',' ',x))

allMoviesIDs = []
allActorsIDs = []
# global actorIndex
# global movieIndex 
actorIndex = 0
movieIndex = 0

class ImdbSpider(scrapy.Spider):
    name = 'imdb'
    allowed_domains = ['www.imdb.com']
    start_urls = ['https://www.imdb.com/title/tt0096463/fullcredits/']
    
    # global allMoviesIDs 
    # global allActorsIDs
    

    
    def parse(self, response):
        global movieIndex
        global actorIndex

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
            if len(actorsInfo.css(".primary_photo a::attr(href)").extract()[i].split('/')) < 1:
                continue
            # logging.log(logging.WARNING, response.css(".primary_photo a::attr(href)").extract()[i].split('/'))

            id = actorsInfo.css(".primary_photo a::attr(href)").extract()[i].split('/')[2]
            role = cleanString(actorsInfo.css(".character a::text").extract()[i])
            actors_roles.append((actor, id, role))
            
            if id not in allActorsIDs: allActorsIDs.append(id)

        # logging.log(logging.WARNING, allActorsIDs)

        # Then we just grab all of the information about the movie
        movie_id = response.url.split('/')[-3]
        movie_name =  response.css(".subnav_heading::text").extract_first()
        movie_year =  response.css("span[class=nobr]::text").extract_first().strip()[1:-1]
        
        if movie_id not in allMoviesIDs: allMoviesIDs.append(movie_id)
        
        movieIndex+=1

        for actor in actors_roles:
            yield {   
                
                "movie_id": movie_id, 
                "movie_name": movie_name, 
                "movie_year": movie_year,
                "actor_name": actor[0], 
                "actor_id": actor[1], 
                "role_name": actor[2]
            }
        # yield response.follow("www.imdb.com/name/" + allActorsIDs[actorIndex] + "/", callback=self.parse_actor)
        # response.follow("www.imdb.com/name/" + allActorsIDs[actorIndex], callback=self.parse_actor)
        logging.log(logging.WARNING, "www.imdb.com/name/" + allActorsIDs[actorIndex] + "/")

        yield scrapy.Request("https://www.imdb.com/name/" + allActorsIDs[actorIndex] + "/", callback=self.parse_actor)


    def parse_actor(self, response):
        global actorIndex
        actorIndex+=1

        # logging.log(logging.WARNING, response.url)
        # logging.log(logging.WARNING, response.css)

        # logging.log(logging.WARNING, response.css(".filmo-category-section").extract())
        listOfMovies = response.css(".filmo-category-section")[0]

        # for movie in listOfMovies:
        # listOfYears = listOfMovies.css(".year_column::text").extract()
        # years = [x[-5:-1] for x in listOfYears]

        for movie in listOfMovies.css(".filmo-row"):
            year = movie.css('.year_column::text').extract_first()[-5:-1]
            
            # We check that the movies is from the 80s
            if len(year) == 4 and year[2] == '8':
                id = movie.css('a::attr(href)').extract_first().split('/')[2]
                if id not in allMoviesIDs:
                    allMoviesIDs.append(id)

        yield scrapy.Request("https://www.imdb.com/title/" + allMoviesIDs[movieIndex] + "/fullcredits", callback=self.parse)

        # x= 1/0