from django.urls import path
from .import views


urlpatterns = [
    path('profile/', views.profileView, name='profile'),
    path('profile_update/', views.profileUpdate, name='update'),
    path('change_password/', views.changePassword, name='change_password'),
]
