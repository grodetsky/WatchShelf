from django.shortcuts import render
from django.http import Http404
from .tmdb_service import get_popular_media, get_total_pages, get_media_details, search_media

VALID_MEDIA_TYPES = {'movie', 'tv'}
MAX_PAGES = 500


def validate_media_type(media_type):
    if media_type not in VALID_MEDIA_TYPES:
        raise Http404(f"Invalid media type: {media_type}")


def index(request):
    return render(request, 'library/index.html')


def catalog_view(request, media_type):
    validate_media_type(media_type)

    total_pages = min(get_total_pages(media_type, 'popular'), MAX_PAGES)
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
        'page_range': page_range,
        'total_pages': total_pages,
    }
    return render(request, 'library/catalog.html', context)


def media_detail_view(request, media_type, media_id):
    validate_media_type(media_type)

    details = get_media_details(media_type, media_id)
    if not details:
        raise Http404("Media not found")

    context = {
        'details': details,
        'title': getattr(details, 'title', getattr(details, 'name', 'Unknown')),
        'media_type': media_type,
    }
    return render(request, 'library/media_detail.html', context)


def search_view(request):
    query = request.GET.get('q', '').strip()
    media_type = request.GET.get('type', 'movie')

    total_pages = min(get_total_pages(media_type, 'search', query), MAX_PAGES)
    try:
        page = max(1, min(int(request.GET.get('page', 1)), total_pages))
    except ValueError:
        page = 1

    search_results = search_media(query, media_type, page)
    page_range = range(max(1, page - 2), min(total_pages, page + 2) + 1)

    context = {
        'query': query,
        'media_type': media_type,
        'search_results': search_results,
        'current_page': page,
        'page_range': page_range,
        'total_pages': total_pages,
    }

    return render(request, 'library/search.html', context)

