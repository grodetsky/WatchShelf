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


def get_popular_media(media_type='movie', page=1):
    try:
        if media_type in MEDIA_TYPES:
            results = MEDIA_TYPES[media_type].popular(page=page)
        else:
            logger.error(f"Invalid media type: {media_type}")
            return []
    except Exception as e:
        logger.error(f"Error fetching popular {media_type} on page {page}: {e}")
        return []

    return [
        {
            'id': item.id,
            'title': getattr(item, 'title', getattr(item, 'name', 'Unknown')),
            'poster_path': item.poster_path
        }
        for item in results
    ]


def get_total_pages(media_type='movie', query_type='popular'):
    if media_type in MEDIA_TYPES:
        media_handler = MEDIA_TYPES[media_type]
        if hasattr(media_handler, query_type):
            query_method = getattr(media_handler, query_type)
            return query_method().total_pages
        else:
            logger.error(f"Invalid query type: {query_type}")
            return 1
    else:
        logger.error(f"Invalid media type: {media_type}")
        return 1


def get_media_details(media_type, media_id):
    try:
        if media_type in MEDIA_TYPES:
            return MEDIA_TYPES[media_type].details(media_id)
        else:
            logger.error(f"Invalid media type: {media_type}")
            return None
    except Exception as e:
        logger.error(f"Error fetching details for {media_type} with id {media_id}: {e}")
        return None


def search_movies(query):
    return movie_api.search(query)


def search_tv_shows(query):
    return tv_api.search(query)
