from django.shortcuts import render
from .tmdb_service import get_popular_media


def index(request):
    return render(request, 'library/index.html')


def catalog_view(request, media_type):
    try:
        page = max(1, min(int(request.GET.get('page', 1)), 500))
    except ValueError:
        page = 1

    page_range = range(max(1, page - 2), min(500, page + 2) + 1)
    media_list = get_popular_media(media_type, page=page)

    context = {
        'media_type': media_type,
        'media_list': media_list,
        'current_page': page,
        'page_range': page_range,
    }
    return render(request, 'library/catalog.html', context)
