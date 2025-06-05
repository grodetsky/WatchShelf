from django.shortcuts import render
from .tmdb_service import get_popular_media, get_total_pages


def index(request):
    return render(request, 'library/index.html')


def catalog_view(request, media_type):
    total_pages = get_total_pages(media_type, 'popular')

    try:
        page = max(1, min(int(request.GET.get('page', 1)), total_pages))
    except ValueError:
        page = 1

    media_list = get_popular_media(media_type, page=page)
    page_range = range(max(1, page - 2), min(total_pages, page + 2) + 1)

    context = {
        'media_type': media_type,
        'media_list': media_list,
        'current_page': page,
        'total_pages': total_pages,
        'page_range': page_range,
        'has_previous': page > 1,
        'has_next': page < total_pages,
        'previous_page': page - 1 if page > 1 else None,
        'next_page': page + 1 if page < total_pages else None,
    }
    return render(request, 'library/catalog.html', context)
