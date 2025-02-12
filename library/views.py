from django.shortcuts import render, redirect, Http404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .tmdb_service import get_popular_media_items, get_media_details

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

    return render(request, 'library/catalog.html', {
        'page_title': PAGE_TITLE_MAP.get(media_type, "Unknown"),
        'items': items,
        'media_type': media_type,
        'current_page': page_number,
        'page_range': page_range,
    })


def media_detail_view(request, media_type, media_id):
    if media_type not in PAGE_TITLE_MAP:
        raise Http404("Invalid media type")

    media = get_media_details(media_type, media_id)

    if not media:
        raise Http404("Media not found")

    media_display = media.get("title") or media.get("name")
    release_date = media.get("release_date") or media.get("first_air_date")

    return render(request, 'library/media_detail.html', {
        'media': media,
        'media_type': media_type,
        'media_display': media_display,
        'release_date': release_date,
    })


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'library/signup.html', {'form': form})
