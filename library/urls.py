from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('movie/', views.catalog_view, {'media_type': 'movie'}, name='movie_catalog'),
    path('movie/<int:media_id>/', views.details_view, {'media_type': 'movie'}, name='movie_details'),
    path('movie/<str:category>/', views.catalog_view, {'media_type': 'movie'}, name='movie_category'),

    path('tv/', views.catalog_view, {'media_type': 'tv'}, name='tv_catalog'),
    path('tv/<int:media_id>/', views.details_view, {'media_type': 'tv'}, name='tv_details'),
    path('tv/<str:category>/', views.catalog_view, {'media_type': 'tv'}, name='tv_category'),

    path('search/<str:media_type>', views.search_view, name='search'),

    path('<str:media_type>/<int:media_id>/status/', views.set_status, name='set_status'),
    path('<str:media_type>/<int:media_id>/remove/', views.remove_status, name='remove_status'),

    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/<str:username>/<str:status>/', views.profile_view, name='profile_status'),
    path('profile/<str:username>/<str:status>/<str:media_type>/', views.profile_view, name='profile_filter'),

    path('collection/<int:collection_id>/', views.collection_detail_view, name='collection_detail'),
    path('collection/create/', views.create_collection_view, name='create_collection'),
    path('collection/<int:collection_id>/delete/', views.delete_collection_view, name='delete_collection'),
    path('<str:media_type>/<int:media_id>/add_to_collection/', views.add_to_collection_view, name='add_to_collection'),
    path('collection/<int:collection_id>/remove/<int:media_id>/', views.remove_from_collection_view,
         name='remove_from_collection'),

    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='library/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
