from datetime import datetime, timedelta
from django.shortcuts import render
from product.models import Product, Category, Images


def homeView(request):
    page = 'home'
    day = datetime.now() - timedelta(hours=24)
    products = Product.objects.filter(create_at__gte=day, status='Published').order_by('-id')[:10]
    product_latest = Product.objects.filter(status='Published').order_by('-id')[:4]
    product_pick = Product.objects.filter(status='Published').order_by('?')[:4]
    context = {
        'page': page,
        'products': products,
        'product_latest': product_latest,
        'product_pick': product_pick,
    }
    return render(request, 'home/index.html', context)
