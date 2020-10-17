from django.contrib import admin
from . models import ShopCart


class ShopCartAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user', 'quantity', 'price', 'amount']
    list_filter = ['user']

    class Meta:
        model = ShopCart


admin.site.register(ShopCart, ShopCartAdmin)
