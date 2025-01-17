from django.shortcuts import render, get_object_or_404, Http404
from .models import Item
from .constants import ITEM_TYPE_MAP, PAGE_TITLE_MAP


def index(request):
    return render(request, 'library/index.html')


def catalog_view(request, media_type):
    media_type_key = media_type.lower()
    if media_type_key not in ITEM_TYPE_MAP:
        raise Http404(f"Unknown media type: {media_type_key}")

    items = Item.objects.filter(item_type=ITEM_TYPE_MAP[media_type_key]).order_by('-created_at')
    page_title = PAGE_TITLE_MAP[media_type_key]

    return render(request, 'library/catalog.html', {
        'items': items,
        'page_title': page_title,
    })


def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    context = {'item': item}
    return render(request, 'library/item_detail.html', context)
