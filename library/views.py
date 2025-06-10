from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth import login
from .forms import SignUpForm
from .tmdb_service import get_media_by_category, search_media, get_total_pages, get_media_details, CATEGORIES


def validate_media_type(media_type):
    if media_type not in CATEGORIES:
        raise Http404(f"Media type '{media_type}' not found")


def validate_category(media_type, category):
    if category not in CATEGORIES[media_type]:
        raise Http404(f"Category '{category}' not available for {media_type}")


def validate_media_id(media_id):
    if not isinstance(media_id, int) or media_id <= 0:
        raise Http404("Invalid media ID")
    return media_id


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


def details_view(request, media_type, media_id):
    validate_media_type(media_type)
    validate_media_id(media_id)

    details = get_media_details(media_type, media_id)
    if not details:
        raise Http404(f"{media_type.title()} with ID={media_id} not found.")

    context = {
        'media_type': media_type,
        'details': details,
    }
    return render(request, 'library/details.html', context)


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
    else:
        form = SignUpForm()
    return render(request, "library/signup.html", {"form": form})
