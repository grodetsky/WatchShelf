from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('movie/', views.catalog_view, {'media_type': 'movie'}, name='movie_catalog'),
    path('tv/', views.catalog_view, {'media_type': 'tv'}, name='tv_catalog'),
]
