from django import template
from product.models import Category
from order.models import ShopCart

register = template.Library()


@register.simple_tag
def categorylist():
    return Category.objects.filter(status='True')


@register.simple_tag
def shopcart(userid):
    product = ShopCart.objects.all()
    return product


@register.simple_tag
def shopcartcount(userid):
    count = ShopCart.objects.filter(user_id=userid).count()
    return count


@register.simple_tag
def totalcount(userid):
    shopcart = ShopCart.objects.filter(user_id=userid)
    total = 0
    for shop in shopcart:
        total += shop.product.price * shop.quantity
    return total
