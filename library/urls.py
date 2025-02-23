from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('movie/', views.catalog_view, {'media_type': 'movie'}, name='movie_catalog'),
    path('movie/<int:media_id>/', views.media_detail_view, {'media_type': 'movie'}, name='movie_detail'),

    path('tv/', views.catalog_view, {'media_type': 'tv'}, name='tv_catalog'),
    path('tv/<int:media_id>/', views.media_detail_view, {'media_type': 'tv'}, name='tv_detail'),

    path('search/', views.search_view, name='search'),
]
