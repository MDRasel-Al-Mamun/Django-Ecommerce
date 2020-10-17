from django.urls import path
from . import views

urlpatterns = [
    path('shopcart/', views.shopCart, name='shopcart'),
    path('addtoshopcart/<int:id>', views.addToShopCart, name='addtoshopcart'),
    path('deleteshopcart/<int:id>', views.deleteShopCart, name='deleteshopcart'),
]
