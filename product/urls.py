from django.urls import path
from .import views

urlpatterns = [
    path('<str:id>/<slug:slug>', views.productDetail, name='product_detail'),
    path('category/<str:id>/<slug:slug>/', views.categoryView, name="category"),
    path('addcomment/<str:id>/<slug:slug>/', views.addComment, name='addcomment'),
]
