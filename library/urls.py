from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('catalog/<str:media_type>/', views.catalog_view, name='catalog_view'),
    path('<str:media_type>/<int:media_id>/', views.media_detail_view, name='media_detail'),
]
