from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
from .models import MediaItem, UserItem
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


def details_view(request, media_type, media_id):
    validate_media_type(media_type)
    validate_media_id(media_id)

    details = get_media_details(media_type, media_id)
    if not details:
        raise Http404(f"{media_type.title()} with ID={media_id} not found.")

    user_item = None
    if request.user.is_authenticated:
        try:
            media_item = MediaItem.objects.get(tmdb_id=media_id, media_type=media_type)
            user_item = UserItem.objects.get(user=request.user, media_item=media_item)
        except (MediaItem.DoesNotExist, UserItem.DoesNotExist):
            pass

    context = {
        'media_type': media_type,
        'details': details,
        'user_item': user_item,
    }
    return render(request, 'library/details.html', context)


@login_required
def set_status(request, media_type, media_id):
    validate_media_type(media_type)
    if request.method != 'POST':
        raise Http404()

    selected_status = request.POST.get('status')
    media_item, _ = MediaItem.objects.get_or_create(
        tmdb_id=media_id,
        media_type=media_type
    )

    if selected_status == 'delete':
        UserItem.objects.filter(user=request.user, media_item=media_item).delete()
        if not UserItem.objects.filter(media_item=media_item).exists():
            media_item.delete()
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

    media_item = get_object_or_404(
        MediaItem,
        tmdb_id=media_id,
        media_type=media_type
    )
    UserItem.objects.filter(user=request.user, media_item=media_item).delete()
    if not UserItem.objects.filter(media_item=media_item).exists():
        media_item.delete()

    return redirect(f"{media_type}_details", media_id=media_id)


@login_required
def profile_view(request, username, status=None, media_type=None):
    if username != request.user.username:
        raise Http404("User not found")

    if status in CATEGORIES and media_type is None:
        media_type, status = status, None

    if status:
        validate_status(status)
    if media_type:
        validate_media_type(media_type)

    qs = UserItem.objects.filter(user=request.user)
    if status:
        qs = qs.filter(status=status)
    if media_type:
        qs = qs.filter(media_item__media_type=media_type)

    items = []
    for ui in qs.select_related('media_item'):
        details = get_media_details(ui.media_item.media_type, ui.media_item.tmdb_id)
        if details:
            items.append({
                'details': details,
                'status': ui.status,
                'media_type': ui.media_item.media_type,
            })

    context = {
        'items': items,
        'current_status': status,
        'current_media_type': media_type,
    }
    return render(request, 'library/profile.html', context)


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
