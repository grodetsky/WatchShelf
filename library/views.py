from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .forms import SignUpForm
from .models import MediaItem, UserItem, Collection
from .tmdb_service import (get_media_by_category, search_media, get_media_by_genre, get_genre_name,
                           get_total_pages, get_media_details, CATEGORIES)


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


def validate_genre_id(genre_id):
    if not isinstance(genre_id, int) or genre_id <= 0:
        raise Http404("Invalid genre ID")
    return genre_id


def validate_status(status):
    if status not in dict(UserItem.STATUS_CHOICES):
        raise Http404(f"Status '{status}' not found")


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


def cleanup_unused_media_item(media_item):
    if (not UserItem.objects.filter(media_item=media_item).exists() and
            not media_item.collection_set.exists()):
        media_item.delete()


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


def genre_view(request, genre_id, media_type):
    validate_media_type(media_type)
    validate_genre_id(genre_id)

    genre_name = get_genre_name(genre_id, media_type)
    total_pages = get_total_pages(media_type, genre_id=genre_id)
    try:
        page = max(1, min(int(request.GET.get('page', 1)), total_pages))
    except ValueError:
        page = 1

    media_list = get_media_by_genre(genre_id, media_type, page=page)
    page_range = range(max(1, page - 2), min(total_pages, page + 2) + 1)

    context = {
        'media_type': media_type,
        'genre_id': genre_id,
        'genre_name': genre_name,
        'media_list': media_list,
        'current_page': page,
        'total_pages': total_pages,
        'page_range': page_range,
        'has_previous': page > 1,
        'has_next': page < total_pages,
        'previous_page': page - 1 if page > 1 else None,
        'next_page': page + 1 if page < total_pages else None,
    }
    return render(request, 'library/genre.html', context)


def details_view(request, media_type, media_id):
    validate_media_type(media_type)
    validate_media_id(media_id)

    details = get_media_details(media_type, media_id)
    if not details:
        raise Http404(f"{media_type.title()} with ID={media_id} not found.")

    user_item = None
    user_collections = []
    media_in_collections = []

    if request.user.is_authenticated:
        try:
            media_item = MediaItem.objects.get(tmdb_id=media_id, media_type=media_type)
            user_item = UserItem.objects.get(user=request.user, media_item=media_item)
        except (MediaItem.DoesNotExist, UserItem.DoesNotExist):
            user_item = None

        user_collections = Collection.objects.filter(user=request.user)
        try:
            media_item = MediaItem.objects.get(tmdb_id=media_id, media_type=media_type)
            media_in_collections = list(
                Collection.objects.filter(user=request.user, media_items=media_item)
                .values_list('id', flat=True)
            )
        except MediaItem.DoesNotExist:
            media_in_collections = []

    context = {
        'media_type': media_type,
        'details': details,
        'user_item': user_item,
        'user_collections': user_collections,
        'media_in_collections': media_in_collections,
    }
    return render(request, 'library/details.html', context)


@login_required
def set_status(request, media_type, media_id):
    validate_media_type(media_type)
    validate_media_id(media_id)

    if request.method != 'POST':
        raise Http404("Method not allowed")

    selected_status = request.POST.get('status')

    with transaction.atomic():
        media_item, created = MediaItem.objects.get_or_create(
            tmdb_id=media_id,
            media_type=media_type
        )

        if selected_status == 'delete':
            UserItem.objects.filter(user=request.user, media_item=media_item).delete()
            cleanup_unused_media_item(media_item)
        elif selected_status in dict(UserItem.STATUS_CHOICES):
            UserItem.objects.update_or_create(
                user=request.user,
                media_item=media_item,
                defaults={'status': selected_status}
            )

    return redirect(f"{media_type}_details", media_id=media_id)


@login_required
def remove_status(request, media_type, media_id):
    validate_media_type(media_type)
    validate_media_id(media_id)

    if request.method != 'POST':
        raise Http404("Method not allowed")

    media_item = get_object_or_404(MediaItem, tmdb_id=media_id, media_type=media_type)

    with transaction.atomic():
        deleted_count, _ = UserItem.objects.filter(user=request.user, media_item=media_item).delete()
        if deleted_count > 0:
            cleanup_unused_media_item(media_item)

    return redirect(f"{media_type}_details", media_id=media_id)


def profile_view(request, username, status=None, media_type=None):
    if username != request.user.username:
        raise Http404("User not found")

    if status == 'collections':
        collections = Collection.objects.filter(user=request.user).order_by('-updated_at')
        context = {
            'items': [],
            'current_status': 'collections',
            'current_media_type': media_type,
            'collections': collections,
            'show_collections': True,
        }
        return render(request, 'library/profile.html', context)

    if status in CATEGORIES and media_type is None:
        media_type, status = status, None

    if status:
        validate_status(status)
    if media_type:
        validate_media_type(media_type)

    user_items = UserItem.objects.filter(user=request.user)
    if status:
        user_items = user_items.filter(status=status)
    if media_type:
        user_items = user_items.filter(media_item__media_type=media_type)

    items = []
    for user_item in user_items.select_related('media_item'):
        details = get_media_details(user_item.media_item.media_type, user_item.media_item.tmdb_id)
        if details:
            items.append({
                'details': details,
                'status': user_item.status,
                'media_type': user_item.media_item.media_type,
            })

    context = {
        'items': items,
        'current_status': status,
        'current_media_type': media_type,
        'show_collections': False,
    }
    return render(request, 'library/profile.html', context)


def collection_detail_view(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)

    items = []
    for media_item in collection.media_items.all():
        details = get_media_details(media_item.media_type, media_item.tmdb_id)
        if details:
            items.append({
                'details': details,
                'media_type': media_item.media_type,
                'media_item': media_item,
            })

    context = {
        'collection': collection,
        'items': items,
    }
    return render(request, 'library/collection_detail.html', context)


@login_required
def create_collection_view(request):
    if request.method != 'POST':
        raise Http404("Method not allowed")

    name = request.POST.get('name', '').strip()
    if not name:
        return redirect('profile_status', username=request.user.username, status='collections')

    if Collection.objects.filter(user=request.user, name=name).exists():
        return redirect('profile_status', username=request.user.username, status='collections')

    add_current_item = request.POST.get('add_current_item') == 'on'
    media_type = request.POST.get('media_type')
    media_id = request.POST.get('media_id')

    with transaction.atomic():
        collection = Collection.objects.create(user=request.user, name=name)

        if add_current_item and media_type and media_id:
            try:
                validate_media_type(media_type)
                media_id = int(media_id)
                validate_media_id(media_id)

                media_item, created = MediaItem.objects.get_or_create(
                    tmdb_id=media_id,
                    media_type=media_type
                )
                collection.media_items.add(media_item)
                collection.save(update_fields=['updated_at'])
            except (ValueError, Http404):
                pass

    return redirect('collection_detail', collection_id=collection.id)


@login_required
def delete_collection_view(request, collection_id):
    if request.method != 'POST':
        raise Http404("Method not allowed")

    collection = get_object_or_404(Collection, id=collection_id, user=request.user)

    with transaction.atomic():
        media_items_to_check = list(collection.media_items.all())
        collection.delete()

        for media_item in media_items_to_check:
            cleanup_unused_media_item(media_item)

    return redirect('profile_status', username=request.user.username, status='collections')


@login_required
def add_to_collection_view(request, media_type, media_id):
    validate_media_type(media_type)
    validate_media_id(media_id)

    if request.method != 'POST':
        raise Http404("Method not allowed")

    collection_id = request.POST.get('collection_id')
    if not collection_id:
        return redirect(f"{media_type}_details", media_id=media_id)

    collection = get_object_or_404(Collection, id=collection_id, user=request.user)

    with transaction.atomic():
        media_item, created = MediaItem.objects.get_or_create(
            tmdb_id=media_id,
            media_type=media_type
        )

        if media_item in collection.media_items.all():
            collection.media_items.remove(media_item)
            cleanup_unused_media_item(media_item)
        else:
            collection.media_items.add(media_item)
            collection.save(update_fields=['updated_at'])

    return redirect(f"{media_type}_details", media_id=media_id)


@login_required
def remove_from_collection_view(request, collection_id, media_id):
    if request.method != 'POST':
        raise Http404("Method not allowed")

    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    media_item = get_object_or_404(MediaItem, tmdb_id=media_id)

    with transaction.atomic():
        collection.media_items.remove(media_item)
        collection.save(update_fields=['updated_at'])
        cleanup_unused_media_item(media_item)

    return redirect('collection_detail', collection_id=collection_id)


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