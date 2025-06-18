import logging
from tmdbv3api import TMDb, Movie, TV, Genre, Discover
from django.conf import settings

logger = logging.getLogger(__name__)

tmdb = TMDb()
tmdb.api_key = settings.TMDB_API_KEY
tmdb.language = "en"

movie_api = Movie()
tv_api = TV()
genre_api = Genre()
discover_api = Discover()

MEDIA_TYPES = {
    'movie': movie_api,
    'tv': tv_api
}

CATEGORIES = {
    'movie': ['popular', 'top_rated', 'upcoming', 'now_playing'],
    'tv': ['popular', 'top_rated', 'on_the_air', 'airing_today']
}

MAX_PAGES = 500


def log_error(error_message, default_value=None):
    logger.error(error_message)
    return default_value


def get_media_handler(media_type):
    if media_type not in MEDIA_TYPES:
        raise ValueError(f"Invalid media type: {media_type}")
    return MEDIA_TYPES[media_type]


def validate_category(media_type, category):
    if media_type not in CATEGORIES:
        raise ValueError(f"Invalid media type: {media_type}")
    if category not in CATEGORIES[media_type]:
        raise ValueError(
            f"Invalid category '{category}' for media type '{media_type}'. Available: {CATEGORIES[media_type]}")
    return True


def get_media_by_category(media_type='movie', category='popular', page=1):
    try:
        validate_category(media_type, category)
        page = max(1, min(page, MAX_PAGES))

        media_handler = get_media_handler(media_type)
        category_method = getattr(media_handler, category)
        results = category_method(page=page)

        return [
            {
                'id': item.id,
                'title': getattr(item, 'title', getattr(item, 'name', 'Unknown')),
                'poster_path': item.poster_path
            }
            for item in results.results
        ]
    except Exception as e:
        return log_error(f"Error fetching {category} {media_type} on page {page}: {e}", [])


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


def get_genres_list(media_type='movie'):
    try:
        if media_type not in MEDIA_TYPES:
            raise ValueError(f"Invalid media type: {media_type}")

        if media_type == 'movie':
            results = genre_api.movie_list()
        else:
            results = genre_api.tv_list()

        return [
            {
                'id': genre['id'],
                'name': genre['name']
            }
            for genre in results['genres']
        ]
    except Exception as e:
        return log_error(f"Error fetching genres for {media_type}: {e}", [])


def get_media_by_genre(genre_id, media_type='movie', page=1):
    try:
        if media_type not in MEDIA_TYPES:
            raise ValueError(f"Invalid media type: {media_type}")

        page = max(1, min(page, MAX_PAGES))

        if media_type == 'movie':
            results = discover_api.discover_movies({
                'with_genres': genre_id,
                'page': page
            })
        else:
            results = discover_api.discover_tv_shows({
                'with_genres': genre_id,
                'page': page
            })

        return [
            {
                'id': item.id,
                'title': getattr(item, 'title', getattr(item, 'name', 'Unknown')),
                'poster_path': item.poster_path
            }
            for item in results.results
        ]
    except Exception as e:
        return log_error(f"Error fetching {media_type} for genre {genre_id} on page {page}: {e}", [])


def get_genre_name(genre_id, media_type='movie'):
    try:
        if media_type not in MEDIA_TYPES:
            raise ValueError(f"Invalid media type: {media_type}")

        genres = get_genres_list(media_type)
        for genre in genres:
            if genre['id'] == genre_id:
                return genre['name']

        other_media_type = 'tv' if media_type == 'movie' else 'movie'
        other_genres = get_genres_list(other_media_type)
        for genre in other_genres:
            if genre['id'] == genre_id:
                return genre['name']

        return f"Genre {genre_id}"
    except Exception as e:
        return log_error(f"Error fetching genre name for {genre_id}: {e}", f"Genre {genre_id}")


def get_total_pages(media_type='movie', category=None, query=None, genre_id=None):
    try:
        if query:
            media_handler = get_media_handler(media_type)
            response = media_handler.search(query, page=1)
        elif genre_id:
            if media_type not in MEDIA_TYPES:
                raise ValueError(f"Invalid media type: {media_type}")

            if media_type == 'movie':
                response = discover_api.discover_movies({
                    'with_genres': genre_id,
                    'page': 1
                })
            else:
                response = discover_api.discover_tv_shows({
                    'with_genres': genre_id,
                    'page': 1
                })
        else:
            validate_category(media_type, category)
            media_handler = get_media_handler(media_type)
            category_method = getattr(media_handler, category)
            response = category_method(page=1)

        return min(response.total_pages, MAX_PAGES)
    except Exception as e:
        return log_error(f"Error fetching total pages for {category} {media_type}: {e}", 1)


def get_media_details(media_type, media_id):
    try:
        media_handler = get_media_handler(media_type)
        return media_handler.details(media_id)
    except Exception as e:
        return log_error(f"Error fetching details for {media_type} id {media_id}: {e}", None)