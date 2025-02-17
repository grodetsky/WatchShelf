from tmdbv3api import TMDb, Movie, TV
from django.conf import settings

tmdb = TMDb()
tmdb.api_key = settings.TMDB_API_KEY
tmdb.language = "en"

movie_api = Movie()
tv_api = TV()


def search_movies(query):
    return movie_api.search(query)


def search_tv_shows(query):
    return tv_api.search(query)


def get_movie_details(movie_id):
    return movie_api.details(movie_id)


def get_tv_details(tv_id):
    return tv_api.details(tv_id)
