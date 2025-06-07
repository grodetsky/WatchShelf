from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('movie/', views.catalog_view, {'media_type': 'movie'}, name='movie_catalog'),
    path('movie/<str:category>/', views.catalog_view, {'media_type': 'movie'}, name='movie_category'),

    path('tv/', views.catalog_view, {'media_type': 'tv'}, name='tv_catalog'),
    path('tv/<str:category>/', views.catalog_view, {'media_type': 'tv'}, name='tv_category'),

    path('search/<str:media_type>', views.search_view, name='search'),
]
