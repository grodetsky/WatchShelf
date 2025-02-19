from django.shortcuts import render
from .tmdb_service import get_popular_media


def index(request):
    return render(request, 'library/index.html')


def catalog_view(request, media_type):
    media_list = get_popular_media(media_type)

    context = {
        'media_type': media_type,
        'media_list': media_list,
    }
    return render(request, 'library/catalog.html', context)
