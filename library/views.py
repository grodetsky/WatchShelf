from django.shortcuts import render
from django.http import Http404
from .tmdb_service import get_media_by_category, search_media, get_total_pages, CATEGORIES


def validate_media_type(media_type):
    if media_type not in CATEGORIES:
        raise Http404(f"Media type '{media_type}' not found")


def validate_category(media_type, category):
    if category not in CATEGORIES[media_type]:
        raise Http404(f"Category '{category}' not available for {media_type}")


def index(request):
    return render(request, 'library/index.html')


def catalog_view(request, media_type, category='popular'):
    validate_media_type(media_type)
    validate_category(media_type, category)

    total_pages = get_total_pages(media_type, category=category)

    try:
        page = max(1, min(int(request.GET.get('page', 1)), total_pages))
    except ValueError:
        page = 1

    media_list = get_media_by_category(media_type, category, page=page)
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
        'category_display': get_category_display_name(category),
    }
    return render(request, 'library/catalog.html', context)


def get_category_display_name(category):
    category_names = {
        'popular': 'Popular',
        'top_rated': 'Top Rated',
        'upcoming': 'Upcoming',
        'now_playing': 'Now Playing',
        'on_the_air': 'On The Air',
        'airing_today': 'Airing Today'
    }
    return category_names.get(category, category.replace('_', ' ').title())


def search_view(request, media_type):
    validate_media_type(media_type)

    query = request.GET.get('query', '').strip()

    total_pages = get_total_pages(media_type, query=query)

    try:
        page = max(1, min(int(request.GET.get('page', 1)), total_pages))
    except ValueError:
        page = 1

    search_results = search_media(query, media_type, page=page)
    page_range = range(max(1, page - 2), min(total_pages, page + 2) + 1)

    context = {
        'query': query,
        'media_type': media_type,
        'search_results': search_results,
        'current_page': page,
        'total_pages': total_pages,
        'page_range': page_range,
        'has_previous': page > 1,
        'has_next': page < total_pages,
        'previous_page': page - 1 if page > 1 else None,
        'next_page': page + 1 if page < total_pages else None,
    }

    return render(request, 'library/search.html', context)
