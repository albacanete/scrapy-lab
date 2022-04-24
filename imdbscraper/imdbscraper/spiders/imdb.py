import scrapy
import unidecode
import re
import logging

cleanString = lambda x: '' if x is None else unidecode.unidecode(re.sub(r'\s+',' ',x))

allMoviesIDs = []
allActorsIDs = []

actorIndex = 0
movieIndex = 0

class ImdbSpider(scrapy.Spider):
    name = 'imdb'
    allowed_domains = ['www.imdb.com']
    start_urls = ['https://www.imdb.com/title/tt0096463/fullcredits/']
    
    def parse(self, response):
        global movieIndex
        global actorIndex

        # We have pairs of actor and role in this table list which we will specify next
        cast = response.css(".cast_list")

        actors_roles =[]

        # We extrat the actors name from the photo's title, the role from the text labeled
        # as character, and the id from the photo's link. We didn't directly get the name 
        # the table because that text isn't well labeled, and we found it quite hard to get
        # this information otherwise since it only has td as label, nothing else.

        # Classes odd and even contain the list of all of the actors and their roles
        for act in cast.css(".odd, .even"):
            # After some tests, we found out that this can be empty, so we just do a verification
            if act.css(".primary_photo img::attr(title)").extract_first() is not None:
                actor = cleanString(act.css(".primary_photo img::attr(title)").extract_first())

                id = act.css(".primary_photo a::attr(href)").extract_first().split('/')[2]
                role = cleanString(act.css(".character a::text").extract_first())
                actors_roles.append((actor, id, role))

                # We store the actor's ID if it is not yey in the list
                if id not in allActorsIDs: allActorsIDs.append(id)


        # Then we just grab all of the information about the movie
        movie_id = response.url.split('/')[-3]
        movie_name =  response.css(".subnav_heading::text").extract_first()
        # We also adding tv series, and these don't have just a year, but a year interval
        # So we take only the release year.
        movie_year =  cleanString(response.css("span[class=nobr]::text").extract_first().strip()[1:-1]).split('-')[0]
        
        if movie_id not in allMoviesIDs: allMoviesIDs.append(movie_id)
        
        movieIndex+=1

        # We save the actor's data
        for actor in actors_roles:
            yield {   
                
                "movie_id": movie_id, 
                "movie_name": movie_name, 
                "movie_year": movie_year,
                "actor_name": actor[0], 
                "actor_id": actor[1], 
                "role_name": actor[2]
            }
        # We go to one of the actors web page and use the function to parse actors
        yield scrapy.Request("https://www.imdb.com/name/" + allActorsIDs[actorIndex] + "/", callback=self.parse_actor)


    def parse_actor(self, response):
        global actorIndex
        global movieIndex

        actorIndex+=1

        # We obtain the actor's movie list
        listOfMovies = response.css(".filmo-category-section")[0]

        for movie in listOfMovies.css(".filmo-row"):
            
            year = movie.css('.year_column::text').extract_first()[2:-1]
            
            # We check that the movies is from the 80s and also do a necessary verification
            # so that the year is actually a year and not a year interval.
            if len(year) == 4 and year[2] == '8':
                id = movie.css('a::attr(href)').extract_first().split('/')[2]

                if id not in allMoviesIDs:
                    allMoviesIDs.append(id)
        
        # For some reason, 'title' might get added as the id of a movie, for some reason we
        # couldn't filter this out for some weird reason, so we just skip it

        while allMoviesIDs[movieIndex] == 'title' : movieIndex+=1

        # We are redirected to the next movie and go back to the parser movie.
        yield scrapy.Request("https://www.imdb.com/title/" + allMoviesIDs[movieIndex] + "/fullcredits", callback=self.parse)
