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

    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='library/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
