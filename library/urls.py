from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('catalog/<str:media_type>/', views.catalog_view, name='catalog_view'),
    path('<str:media_type>/<int:media_id>/', views.media_detail_view, name='media_detail'),

    path('login/', auth_views.LoginView.as_view(template_name='library/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
]
