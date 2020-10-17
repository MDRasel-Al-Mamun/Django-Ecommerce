from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from order.models import ShopCart, ShopCartForm
from product.models import Category, Product


@login_required(login_url='signin')
def addToShopCart(request, id):
    url = request.META.get('HTTP_REFERER')
    current_user = request.user
    checkproduct = ShopCart.objects.filter(product_id=id)

    if checkproduct:
        control = 1
    else:
        control = 0

    if request.method == 'POST':
        form = ShopCartForm(request.POST)
        if form.is_valid():
            if control == 1:
                data = ShopCart.objects.get(product_id=id)
                data.quantity += form.cleaned_data['quantity']
                data.save()
            else:
                data = ShopCart()
                data.user_id = current_user.id
                data.product_id = id
                data.quantity = form.cleaned_data['quantity']
                data.save()
        return HttpResponseRedirect(url)

    else:
        if control == 1:
            data = ShopCart.objects.get(product_id=id)
            data.quantity += 1
            data.save()
        else:
            data = ShopCart()
            data.user_id = current_user.id
            data.product_id = id
            data.quantity = 1
            data.save()
        return HttpResponseRedirect(url)


@login_required(login_url='signin')
def shopCart(request):
    current_user = request.user
    shopcart = ShopCart.objects.filter(user_id=current_user.id)
    total = 0
    for cart in shopcart:
        total += cart.product.price * cart.quantity

    context = {
        'shopcart': shopcart,
        'total': total,
    }
    return render(request, 'order/cart.html', context)


@login_required(login_url='signin')
def deleteShopCart(request, id):
    url = request.META.get('HTTP_REFERER')
    ShopCart.objects.filter(id=id).delete()
    return HttpResponseRedirect(url)
