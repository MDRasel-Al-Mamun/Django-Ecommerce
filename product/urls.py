from django.urls import path
from .import views

urlpatterns = [
    path('category/<str:id>/<slug:slug>/', views.categoryView, name="category"),
]
