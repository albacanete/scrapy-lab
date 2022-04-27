import scrapy
import unidecode
import re
import os
import uuid
import time
from elasticsearch import Elasticsearch

ELASTIC_API_URL_HOST = os.environ['ELASTIC_API_URL_HOST']
ELASTIC_API_USERNAME = os.environ['ELASTIC_API_USERNAME']
ELASTIC_API_PASSWORD = os.environ['ELASTIC_API_PASSWORD']
es = Elasticsearch(ELASTIC_API_URL_HOST, basic_auth=(ELASTIC_API_USERNAME, ELASTIC_API_PASSWORD))

cleanString = lambda x: '' if x is None else unidecode.unidecode(re.sub(r'\s+', ' ', x))

allMoviesIDs = []
allActorsIDs = []
actorsAges = {}

actorIndex = 0
movieIndex = 0
actorID = 0


class ImdbSpider(scrapy.Spider):
    name = 'imdb'
    allowed_domains = ['www.imdb.com']
    start_urls = ['https://www.imdb.com/title/tt0096463/fullcredits/']
    actor_id = 0

    def parse(self, response):
        global movieIndex
        global actorIndex
        global actorsAges
        global actorID

        # We have pairs of actor and role in this table list which we will specify next
        cast = response.css(".cast_list")

        actors_roles = []

        # We extract the actors name from the photo's title, the role from the text labeled
        # as character, and the id from the photo's link. We didn't directly get the name
        # the table because that text isn't well labeled, and we found it quite hard to get
        # this information otherwise since it only has td as label, nothing else.

        # Classes odd and even contain the list of all of the actors and their roles
        for act in cast.css(".odd, .even"):
            # After some tests, we found out that this can be empty, so we just do a verification
            if act.css(".primary_photo img::attr(title)").extract_first() is not None:
                actor = cleanString(act.css(".primary_photo img::attr(title)").extract_first())

                actorID = act.css(".primary_photo a::attr(href)").extract_first().split('/')[2]
                role = cleanString(act.css(".character a::text").extract_first())
                actors_roles.append((actor, id, role))

                # We store the actor's ID if it is not yey in the list
                if actorID not in allActorsIDs: allActorsIDs.append(actorID)

                #yield scrapy.Request("https://www.imdb.com/name/" + actorID + "/", callback=self.parse_age)

        # Then we just grab all of the information about the movie
        movie_id = response.url.split('/')[-3]
        movie_name = response.css(".subnav_heading::text").extract_first()
        # We also adding tv series, and these don't have just a year, but a year interval
        # So we take only the release year.
        movie_year = cleanString(response.css("span[class=nobr]::text").extract_first().strip()[1:-1]).split('-')[0]

        if movie_id not in allMoviesIDs: allMoviesIDs.append(movie_id)
        movieIndex += 1

        ## TASK 7.2
        # We save the actor's data
        # for actor in actors_roles:
        #    yield {
        #        "movie_id": movie_id,
        #        "movie_name": movie_name,
        #        "movie_year": movie_year,
        #        "actor_name": actor[0],
        #        "actor_id": actor[1],
        #        "role_name": actor[2]
        #    }

        ## TASK 7.3.1
        # We save the actor's data
        # for actor in actors_roles:
        #    es.index(index='imdb_movies',
        #             id=uuid.uuid4(),
        #             body={
        #                 "movie_id": movie_id,
        #                 "movie_name": movie_name,
        #                 "movie_year": movie_year,
        #                 "actor_name": actor[0],
        #                 "actor_id": actor[1],
        #                 "role_name": actor[2]
        #             })

        # We save the actor's data
        for actor in actors_roles:
            yield {
                "movie_id": movie_id,
                "movie_name": movie_name,
                "movie_year": movie_year,
                "actor_name": actor[0],
                "actor_id": actor[1],
                "role_name": actor[2],
                "actor_age": age
            }

        # We go to one of the actors web page and use the function to parse actors
        yield scrapy.Request("https://www.imdb.com/name/" + allActorsIDs[actorIndex] + "/",
                             callback=self.parse_actor)

    # TASK 7.3.2
    def parse_age(self, response):
        global actorsAges
        global actorID

        actorBirthInfo = response.css("#name-born-info")
        actorBirthDate = actorBirthInfo.css('time::attr(datetime)').get()

        if actorBirthDate is not None:
            yearBirth = actorBirthDate.split("-")[0]
            actorsAges[actorID] = yearBirth

    def parse_actor(self, response):
        global actorIndex
        global movieIndex

        actorIndex += 1

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

        while allMoviesIDs[movieIndex] == 'title': movieIndex += 1

        actorBirthInfo = response.css("#name-born-info")
        actorBirthDate = actorBirthInfo.css('time::attr(datetime)').get()

        if actorBirthDate is not None:
            yearBirth = actorBirthDate.split("-")[0]
            actorsAges[actorID] = yearBirth


        # We are redirected to the next movie and go back to the parser movie.
        yield scrapy.Request("https://www.imdb.com/title/" + allMoviesIDs[movieIndex] + "/fullcredits",
                             callback=self.parse)
