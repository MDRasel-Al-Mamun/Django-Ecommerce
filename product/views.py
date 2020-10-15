from django.shortcuts import render
from .models import Product, Category, Images, Comment, CommentForm
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator


def categoryView(request, id, slug):
    category = get_object_or_404(Category, id=id, slug=slug)
    products = Product.objects.filter(category=category, status='Published')
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'product/category.html', context)


def productDetail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug)
    images = Images.objects.filter(product=product)
    product_pick = Product.objects.filter(status='Published').order_by('?')[:4]
    comments = Comment.objects.filter(product=product)
    paginator = Paginator(comments, 5)
    page_number = request.GET.get('page', 1)
    comment_page = paginator.get_page(page_number)
    if comment_page.has_next():
        next_url = f'?page={comment_page.next_page_number()}'
    else:
        next_url = ''
    if comment_page.has_previous():
        prev_url = f'?page={comment_page.previous_page_number()}'
    else:
        prev_url = ''
    context = {
        'product': product,
        'images': images,
        'product_pick': product_pick,
        'comments': comments,
        'comment_page': comment_page,
        'next_page_url': next_url,
        'prev_page_url': prev_url,

    }
    return render(request, 'product/product_detail.html', context)


def addComment(request, id, slug):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            data = Comment()
            data.subject = form.cleaned_data['subject']
            data.comment = form.cleaned_data['comment']
            data.rate = form.cleaned_data['rate']
            data.ip = request.META.get('REMOTE_ADDR')
            data.product_id = id
            current_user = request.user
            data.user_id = current_user.id
            data.save()
            messages.success(request, "Your review has been sent. Thank you for your interest.")
            return HttpResponseRedirect(url)

    return HttpResponseRedirect(url)
