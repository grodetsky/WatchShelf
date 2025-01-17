from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/<str:media_type>/', views.catalog_view, name='catalog_view'),
    path('items/<int:pk>/', views.item_detail, name='item_detail'),
]
