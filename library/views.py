from django.shortcuts import render, get_object_or_404, Http404
from .tmdb_service import get_popular_media_items

PAGE_TITLE_MAP = {
    'movie': "Movies",
    'tv': "TV Series",
    'anime': "Anime",
}


def index(request):
    return render(request, 'library/index.html')


def catalog_view(request, media_type):
    if media_type not in PAGE_TITLE_MAP:
        raise Http404("Invalid media type")

    items = get_popular_media_items(media_type)
    items = [{**item, "display_title": item.get("title") or item.get("name")} for item in items]
    page_title = PAGE_TITLE_MAP[media_type]

    return render(request, 'library/catalog.html', {
        'items': items,
        'page_title': page_title,
    })
