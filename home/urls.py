from django.urls import path
from .import views

urlpatterns = [
    path('', views.homeView, name='home'),
    path('search/', views.searchView, name='search'),
    path('search_auto/', views.searchAuto, name='search_auto'),
]
