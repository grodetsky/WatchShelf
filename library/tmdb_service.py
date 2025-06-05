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

MAX_PAGES = 500


def log_error(error_message, default_value=None):
    logger.error(error_message)
    return default_value


def get_media_handler(media_type):
    if media_type not in MEDIA_TYPES:
        raise ValueError(f"Invalid media type: {media_type}")
    return MEDIA_TYPES[media_type]


def get_popular_media(media_type='movie', page=1):
    try:
        page = max(1, min(page, MAX_PAGES))

        media_handler = get_media_handler(media_type)
        results = media_handler.popular(page=page)
        return [
            {
                'id': item.id,
                'title': getattr(item, 'title', getattr(item, 'name', 'Unknown')),
                'poster_path': item.poster_path
            }
            for item in results.results
        ]
    except Exception as e:
        return log_error(f"Error fetching popular {media_type} on page {page}: {e}", [])


def get_total_pages(media_type='movie', category='popular'):
    try:
        media_handler = get_media_handler(media_type)
        category_method = getattr(media_handler, category)
        response = category_method(page=1)

        return min(response.total_pages, MAX_PAGES)
    except Exception as e:
        return log_error(f"Error fetching total pages for {category} {media_type}: {e}", 1)


def search_movies(query):
    return movie_api.search(query)


def search_tv_shows(query):
    return tv_api.search(query)


def get_movie_details(movie_id):
    return movie_api.details(movie_id)


def get_tv_details(tv_id):
    return tv_api.details(tv_id)
