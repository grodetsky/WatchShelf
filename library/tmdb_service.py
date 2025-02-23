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


def get_popular_media(media_type='movie', page=1):
    try:
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


def get_total_pages(media_type='movie', query_type='popular'):
    try:
        media_handler = get_media_handler(media_type)
        if not hasattr(media_handler, query_type):
            return log_error(f"Invalid query type: {query_type}", 1)
        query_method = getattr(media_handler, query_type)
        return query_method().total_pages
    except Exception as e:
        return log_error(f"Error fetching total pages for {media_type} using {query_type}: {e}", 1)


def get_media_details(media_type, media_id):
    try:
        media_handler = get_media_handler(media_type)
        return media_handler.details(media_id)
    except Exception as e:
        return log_error(f"Error fetching details for {media_type} with id {media_id}: {e}", None)


def search_media(query, media_type='movie', page=1):
    try:
        media_handler = get_media_handler(media_type)
        results = media_handler.search(query, page=page)
        return [
            {
                'id': item.id,
                'title': getattr(item, 'title', getattr(item, 'name', 'Unknown')),
                'poster_path': item.poster_path
            }
            for item in results.results
        ]
    except Exception as e:
        return log_error(f"Error searching {media_type} for query '{query}': {e}", [])
