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


def log_error(error_message, default_value=None):
    logger.error(error_message)
    return default_value


def get_media_handler(media_type):
    if media_type not in MEDIA_TYPES:
        raise ValueError(f"Invalid media type: {media_type}")
    return MEDIA_TYPES[media_type]


def get_popular_media(media_type='movie'):
    try:
        media_handler = get_media_handler(media_type)
        results = media_handler.popular()
        return [
            {
                'id': item.id,
                'title': getattr(item, 'title', getattr(item, 'name', 'Unknown')),
                'poster_path': item.poster_path
            }
            for item in results.results
        ]
    except Exception as e:
        return log_error(f"Error fetching popular {media_type}: {e}", [])


def search_movies(query):
    return movie_api.search(query)


def search_tv_shows(query):
    return tv_api.search(query)


def get_movie_details(movie_id):
    return movie_api.details(movie_id)


def get_tv_details(tv_id):
    return tv_api.details(tv_id)
