from tmdbv3api import TMDb, Movie, TV
import os

tmdb = TMDb()
tmdb.api_key = os.getenv('TMDB_API_KEY')

movie_api = Movie()
tv_api = TV()


def get_popular_media_items(media_type="movie"):
    try:
        if media_type == "movie":
            return movie_api.popular()
        elif media_type == "tv":
            return tv_api.popular()
    except Exception as e:
        print(f"Error fetching TMDb data: {e}")
        return []

    return []
