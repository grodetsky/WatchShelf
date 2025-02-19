from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('<str:media_type>/', views.catalog_view, name='catalog'),
    path('<str:media_type>/<int:media_id>/', views.media_detail_view, name='media_detail'),
]
