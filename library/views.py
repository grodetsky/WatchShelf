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

    page_number = max(1, min(int(request.GET.get('page', 1)), 500))
    page_range = range(max(1, page_number - 1), min(501, page_number + 2))

    items = get_popular_media_items(media_type, page=page_number)
    items = [{**item, "display_title": item.get("title") or item.get("name")} for item in items]

    return render(request, 'library/catalog.html', {
        'items': items,
        'page_title': PAGE_TITLE_MAP.get(media_type, "Unknown"),
        'current_page': page_number,
        'page_range': page_range,
    })
