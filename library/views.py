from django.shortcuts import render
from django.http import Http404
from .tmdb_service import get_popular_media, get_media_details

VALID_MEDIA_TYPES = {'movie', 'tv'}


def validate_media_type(media_type):
    if media_type not in VALID_MEDIA_TYPES:
        raise Http404(f"Invalid media type: {media_type}")


def index(request):
    return render(request, 'library/index.html')


def catalog_view(request, media_type):
    validate_media_type(media_type)

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
