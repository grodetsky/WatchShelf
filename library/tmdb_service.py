import logging
from tmdbv3api import TMDb, Movie, TV
from django.conf import settings

logger = logging.getLogger(__name__)

tmdb = TMDb()
tmdb.api_key = settings.TMDB_API_KEY
tmdb.language = "en"

movie_api = Movie()
tv_api = TV()

MEDIA_TYPES = {
    'movie': movie_api,
    'tv': tv_api
}


def get_popular_media(media_type='movie'):
    try:
        if media_type in MEDIA_TYPES:
            results = MEDIA_TYPES[media_type].popular()
        else:
            logger.error(f"Invalid media type: {media_type}")
            return []
    except Exception as e:
        logger.error(f"Error fetching popular {media_type}: {e}")
        return []

    return [
        {
            "id": item.id,
            "title": item.title if media_type == "movie" else item.name,
            "poster_path": item.poster_path
        }
        for item in results
    ]


def search_movies(query):
    return movie_api.search(query)


def search_tv_shows(query):
    return tv_api.search(query)


def get_movie_details(movie_id):
    return movie_api.details(movie_id)


def get_tv_details(tv_id):
    return tv_api.details(tv_id)
