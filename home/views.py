import json
from django.utils import timezone
from django.shortcuts import render
from product.models import Product, Category, Images
from .forms import SearchForm
from django.http import HttpResponse, HttpResponseRedirect


def homeView(request):
    page = 'home'
    day = timezone.now() - timezone.timedelta(hours=100)
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


def searchView(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            catid = form.cleaned_data['catid']
            if catid == 0:
                products = Product.objects.filter(title__icontains=query)
            else:
                products = Product.objects.filter(title__icontains=query, category_id=catid)
            context = {
                'products': products,
                'query': query,
            }
            return render(request, 'home/search.html', context)

    return HttpResponseRedirect('/')


def searchAuto(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        products = Product.objects.filter(title__icontains=q)

        results = []
        for product in products:
            product_json = {}
            product_json = product.title
            results.append(product_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
