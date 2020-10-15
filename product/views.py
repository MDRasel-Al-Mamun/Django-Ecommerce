from django.shortcuts import render
from .models import Product, Category, Images
from django.shortcuts import render, get_object_or_404


def categoryView(request, id, slug):
    category = get_object_or_404(Category, id=id, slug=slug)
    products = Product.objects.filter(category=category, status='Published')
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'product/category.html', context)
