from django.shortcuts import render, redirect, get_object_or_404, Http404
from .forms import CustomUserCreationForm
from django.contrib import messages
from .models import Item
from .constants import ITEM_TYPE_MAP, PAGE_TITLE_MAP


def index(request):
    return render(request, 'library/index.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created. You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'library/register.html', {'form': form})


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
