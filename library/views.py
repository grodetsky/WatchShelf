from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .forms import SignUpForm
from .models import MediaItem, UserItem, Collection
from .tmdb_service import (get_media_by_category, search_media, get_media_by_genre, get_genre_name,
                           get_total_pages, get_media_details, get_person_details, CATEGORIES)


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


def validate_person_id(person_id):
    if not isinstance(person_id, int) or person_id <= 0:
        raise Http404("Invalid person ID")
    return person_id


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


def process_crew_data(details, media_type):
    crew = {}
    important_jobs = ['Director', 'Writer', 'Screenplay', 'Novel', 'Story', 'Creator', 'Characters']

    if media_type == 'tv' and hasattr(details, 'created_by'):
        for person in details.created_by:
            crew.setdefault(person.name, {
                'id': person.id,
                'name': person.name,
                'profile_path': getattr(person, 'profile_path', None),
                'jobs': []
            })['jobs'].append('Creator')

    crew_list = (getattr(details, 'credits', None) or getattr(details, 'aggregate_credits', None))
    if crew_list:
        for person in getattr(crew_list, 'crew', []):
            if person.job in important_jobs:
                crew.setdefault(person.name, {
                    'id': person.id,
                    'name': person.name,
                    'profile_path': getattr(person, 'profile_path', None),
                    'jobs': []
                })['jobs'].append(person.job)

    processed_crew = [
        {
            'id': p['id'],
            'name': p['name'],
            'profile_path': p['profile_path'],
            'job': ', '.join(p['jobs']),
        }
        for p in crew.values()
    ]
    return processed_crew


def build_credits_list(credits):
    items = []
    for credit in credits.values():
        acting = [r['character'] for r in credit['roles'] if r['role_type'] == 'Acting']
        other = [r['character'] for r in credit['roles'] if r['role_type'] != 'Acting']
        combined = []
        if acting:
            combined.append(' / '.join(acting))
        combined.extend(other)
        credit['combined_roles'] = ' / '.join(combined) if combined else 'Unknown Role'
        items.append(credit)
    return sorted(items, key=lambda c: c['release_date'] or '0000-00-00', reverse=True)


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
    processed_crew = None

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

        processed_crew = process_crew_data(details, media_type)

    context = {
        'media_type': media_type,
        'details': details,
        'user_item': user_item,
        'user_collections': user_collections,
        'media_in_collections': media_in_collections,
        'processed_crew': processed_crew,
    }
    return render(request, 'library/details.html', context)


def cast_view(request, media_type, media_id):
    validate_media_type(media_type)
    validate_media_id(media_id)

    details = get_media_details(media_type, media_id)
    if not details:
        raise Http404(f"{media_type.title()} with ID={media_id} not found.")

    if media_type == 'tv':
        cast_list = getattr(details.aggregate_credits, 'cast', [])
    else:
        cast_list = getattr(details.credits, 'cast', [])

    context = {
        'media_type': media_type,
        'details': details,
        'cast_list': cast_list,
        'cast_count': len(cast_list),
    }
    return render(request, 'library/cast.html', context)


def person_view(request, person_id):
    validate_person_id(person_id)

    person = get_person_details(person_id)
    if not person:
        raise Http404(f"Person with ID={person_id} not found.")

    movie_credits, tv_credits = {}, {}

    for section, role_type, label in [
        ('cast', 'character', 'Acting'),
        ('crew', 'job', None),
    ]:
        for credit in getattr(getattr(person, 'combined_credits', None), section, []):
            ctype = getattr(credit, 'media_type', None)
            cid = credit.id
            role = getattr(credit, role_type, '')
            department = label or getattr(credit, 'department', 'Crew')

            if not ctype or not role:
                continue

            credits = movie_credits if ctype == 'movie' else tv_credits
            if cid not in credits:
                credits[cid] = {
                    'id': cid,
                    'title': getattr(credit, 'title', getattr(credit, 'name', 'Unknown')),
                    'poster_path': getattr(credit, 'poster_path', None),
                    'release_date': getattr(credit, 'release_date', getattr(credit, 'first_air_date', '')),
                    'vote_average': getattr(credit, 'vote_average', 0),
                    'roles': []
                }
            credits[cid]['roles'].append({'character': role, 'role_type': department})

    context = {
        'person_details': person,
        'movie_credits': build_credits_list(movie_credits),
        'tv_credits': build_credits_list(tv_credits),
    }
    return render(request, 'library/person.html', context)


def media_view(request, media_type, media_id):
    validate_media_type(media_type)
    validate_media_id(media_id)

    details = get_media_details(media_type, media_id)
    if not details:
        raise Http404(f"{media_type.title()} with ID={media_id} not found.")

    context = {
        'media_type': media_type,
        'details': details,
    }
    return render(request, 'library/media.html', context)


@login_required
def set_status(request, media_type, media_id):
    validate_media_type(media_type)
    validate_media_id(media_id)

    if request.method != 'POST':
        raise Http404("Method not allowed")

    selected_status = request.POST.get('status')

    with transaction.atomic():
        media_item, _ = MediaItem.objects.get_or_create(
            tmdb_id=media_id,
            media_type=media_type
        )

        if selected_status == 'delete':
            try:
                user_item = UserItem.objects.get(user=request.user, media_item=media_item)
            except UserItem.DoesNotExist:
                pass
            else:
                if user_item.is_favorite:
                    user_item.status = None
                    user_item.save(update_fields=['status'])
                else:
                    user_item.delete()
                    cleanup_unused_media_item(media_item)

        elif selected_status in dict(UserItem.STATUS_CHOICES):
            UserItem.objects.update_or_create(
                user=request.user,
                media_item=media_item,
                defaults={'status': selected_status}
            )

    redirect_url = request.POST.get('redirect_url') or request.META.get('HTTP_REFERER')
    if redirect_url:
        return redirect(redirect_url)
    return redirect(f"{media_type}_details", media_id=media_id)


@login_required
def toggle_favorite(request, media_type, media_id):
    validate_media_type(media_type)
    validate_media_id(media_id)

    if request.method == 'POST':
        with transaction.atomic():
            media_item, _ = MediaItem.objects.get_or_create(
                tmdb_id=media_id,
                media_type=media_type
            )

            user_item, _ = UserItem.objects.get_or_create(
                user=request.user,
                media_item=media_item
            )

            user_item.is_favorite = not user_item.is_favorite

            if not user_item.is_favorite and not user_item.status:
                user_item.delete()
                cleanup_unused_media_item(media_item)
            else:
                user_item.save()

    redirect_url = request.POST.get('redirect_url') or request.META.get('HTTP_REFERER')
    if redirect_url:
        return redirect(redirect_url)
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

    redirect_url = request.POST.get('redirect_url') or request.META.get('HTTP_REFERER')
    if redirect_url:
        return redirect(redirect_url)
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

    if status == 'favorites':
        user_items = UserItem.objects.filter(user=request.user, is_favorite=True)
    elif status:
        validate_status(status)
        user_items = UserItem.objects.filter(user=request.user, status=status)
    else:
        user_items = UserItem.objects.filter(user=request.user)

    if media_type:
        validate_media_type(media_type)
        user_items = user_items.filter(media_item__media_type=media_type)

    user_cols = list(Collection.objects.filter(user=request.user).only('id', 'name'))

    items = []
    for user_item in user_items.select_related('media_item'):
        details = get_media_details(user_item.media_item.media_type, user_item.media_item.tmdb_id)
        if details:
            media_in_cols = list(
                Collection.objects.filter(user=request.user, media_items=user_item.media_item)
                .values_list('id', flat=True)
            )
            items.append({
                'details': details,
                'status': user_item.status,
                'is_favorite': user_item.is_favorite,
                'media_type': user_item.media_item.media_type,
                'user_collections': user_cols,
                'media_in_collections': media_in_cols,
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

    user_cols = list(Collection.objects.filter(user=request.user).exclude(id=collection.id).only('id', 'name'))

    items = []
    for media_item in collection.media_items.all():
        details = get_media_details(media_item.media_type, media_item.tmdb_id)
        if details:
            ui = UserItem.objects.filter(user=request.user, media_item=media_item).first()
            status = ui.status if ui else None
            is_favorite = ui.is_favorite if ui else False
            media_in_cols = list(
                Collection.objects.filter(user=request.user, media_items=media_item)
                .values_list('id', flat=True)
            )

            items.append({
                'details': details,
                'media_type': media_item.media_type,
                'media_item': media_item,
                'status': status,
                'is_favorite': is_favorite,
                'user_collections': user_cols,
                'media_in_collections': media_in_cols,
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

                media_item, _ = MediaItem.objects.get_or_create(
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
        redirect_url = request.POST.get('redirect_url') or request.META.get('HTTP_REFERER')
        if redirect_url:
            return redirect(redirect_url)
        return redirect(f"{media_type}_details", media_id=media_id)

    collection = get_object_or_404(Collection, id=collection_id, user=request.user)

    with transaction.atomic():
        media_item, _ = MediaItem.objects.get_or_create(
            tmdb_id=media_id,
            media_type=media_type
        )

        if media_item in collection.media_items.all():
            collection.media_items.remove(media_item)
            cleanup_unused_media_item(media_item)
        else:
            collection.media_items.add(media_item)
            collection.save(update_fields=['updated_at'])

    redirect_url = request.POST.get('redirect_url') or request.META.get('HTTP_REFERER')
    if redirect_url:
        return redirect(redirect_url)
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

    redirect_url = request.POST.get('redirect_url') or request.META.get('HTTP_REFERER')
    if redirect_url:
        return redirect(redirect_url)
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
