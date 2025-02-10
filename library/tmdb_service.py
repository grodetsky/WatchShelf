import os
import logging
from tmdbv3api import TMDb, Movie, TV

tmdb = TMDb()
tmdb.api_key = os.getenv('TMDB_API_KEY')

movie_api = Movie()
tv_api = TV()

logger = logging.getLogger(__name__)

MEDIA_TYPES = {
    'MOVIE': 'movie',
    'TV': 'tv',
}


def get_popular_media_items(media_type=MEDIA_TYPES['MOVIE'], page=1):
    try:
        if media_type == MEDIA_TYPES['MOVIE']:
            results = movie_api.popular(page=page)
        elif media_type == MEDIA_TYPES['TV']:
            results = tv_api.popular(page=page)
        else:
            return []
    except Exception as e:
        logger.error(f"Error fetching TMDb data: {e}")
        return []

    return [
        {
            "id": item.id,
            "display_title": item.title if media_type == MEDIA_TYPES['MOVIE'] else item.name,
            "poster_path": item.poster_path,
            "release_date": item.release_date if media_type == MEDIA_TYPES['MOVIE'] else item.first_air_date,
            "vote_average": item.vote_average,
        }
        for item in results
    ]


def get_media_details(media_type, media_id):
    try:
        if media_type == MEDIA_TYPES['MOVIE']:
            return movie_api.details(media_id)
        elif media_type == MEDIA_TYPES['TV']:
            return tv_api.details(media_id)
    except Exception as e:
        logger.error(f"Error fetching TMDb details: {e}")
        return []
