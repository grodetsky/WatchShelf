from .models import ItemType

ITEM_TYPE_MAP = {
    'movies': ItemType.MOVIE,
    'anime': ItemType.ANIME,
    'tvseries': ItemType.TV_SERIES,
}

PAGE_TITLE_MAP = {
    'movies': "Movies",
    'anime': "Anime",
    'tvseries': "TV Series",
}
