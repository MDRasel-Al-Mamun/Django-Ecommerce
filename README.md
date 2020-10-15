# Django E-Commerce Website

To Create a Full Ecommerce Website with Django

> - <a href="#model">1. Category & Product Model Setup </a>

> - <a href="#category">2. Show All Nested Category In Navbar </a>

> - <a href="#products">3. Show All Products </a>


## 1. Category & Product Model Setup <a href="" name="model"> - </a>

> - <a href="#category_model">I. Nested Category Model with MPTT </a>

> - <a href="#tinymce">II. Install TinyMCE Editor </a>

> - <a href="#product">III. Create Product Model with Multiple Images </a>


### I. Nested Category Model with MPTT <a href="" name="category_model"> - </a>

1. Create a product app `python manage.py startapp product`

2. Define install app - ecommerce > settings > base.py - `INSTALLED_APPS = ['product.apps.ProductConfig']`

3. Create url - ecommerce > urls.py - `path('product/', include('product.urls'))`

4. Create url file - `product > urls.py`

5. Install MPTT module - `pip install django-mptt`

6. Define MPTT app - ecommerce > settings > base.py - `INSTALLED_APPS = ['mptt']`


* product > models.py

```py
from django.db import models
from django.urls import reverse
from mptt.models import MPTTModel
from mptt.fields import TreeForeignKey


class Category(MPTTModel):
    STATUS = (
        ('True', 'True'),
        ('False', 'False'),
    )
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    keywords = models.CharField(max_length=255, blank=True)
    description = models.TextField(max_length=255, blank=True)
    image = models.ImageField(blank=True, upload_to='category/%Y/%m/%d/')
    status = models.CharField(max_length=10, choices=STATUS)
    slug = models.SlugField(null=False, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.title

    class MPTTMeta:
        order_insertion_by = ['title']

    def __str__(self):
        full_path = [self.title]
        k = self.parent
        while k is not None:
            full_path.append(k.title)
            k = k.parent
        return ' / '.join(full_path[::-1])
    
    def get_absolute_url(self):
        return reverse('category', kwargs={'id': self.id, 'slug': self.slug})
```

* product > admin.py

```py
from .models import *
from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin


class CategoryAdminMptt(DraggableMPTTAdmin):
    mptt_indent_field = "title"
    list_display = ('tree_actions', 'indented_title', 'related_products_count', 'related_products_cumulative_count')
    list_display_links = ('indented_title',)
    search_fields = ['__str__', 'title']
    prepopulated_fields = {'slug': ('title',)}

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        qs = Category.objects.add_related_count(qs, Product, 'category', 'products_cumulative_count', cumulative=True)

        qs = Category.objects.add_related_count(qs, Product, 'category', 'products_count', cumulative=False)
        return qs

    def related_products_count(self, instance):
        return instance.products_count
    related_products_count.short_description = 'Related products (for this specific category)'

    def related_products_cumulative_count(self, instance):
        return instance.products_cumulative_count
    related_products_cumulative_count.short_description = 'Related products (in tree)'


admin.site.register(Category, CategoryAdminMptt)
```


### II. Install TinyMCE Editor <a href="" name="tinymce"> - </a>

1. Install TinyMCE module - `pip install django-filebrowser-no-grappelli django-tinymce4-lite jsmin Pillow pytz`

* ecommerce > settings > base.py

```python
INSTALLED_APPS = [
    'filebrowser',   # Add top of the INSTALLED APPS
    'django.contrib.admin',

    'tinymce',
]
TINYMCE_DEFAULT_CONFIG = {
    'height': 360,
    'width': 970,
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea',
    'theme': 'modern',
    'plugins':
    '''
            textcolor save link image imagetools media preview codesample contextmenu
            table code lists fullscreen  insertdatetime  nonbreaking
            contextmenu directionality searchreplace wordcount visualblocks
            visualchars code fullscreen autolink lists  charmap print  hr
            anchor pagebreak
            ''',
    'toolbar1':
    '''
            fullscreen preview bold italic underline | fontselect,
            fontsizeselect  | forecolor backcolor | alignleft alignright |
            aligncenter alignjustify | indent outdent | bullist numlist table |
            | link image media | codesample |
            ''',
    'toolbar2':
    '''
            visualblocks visualchars |
            charmap hr pagebreak nonbreaking anchor |  code |
            ''',
    'contextmenu': 'formats | link image',
    'menubar': True,
    'statusbar': True,
}
```
* ecommerce > urls.py

```python
from filebrowser.sites import site
from django.urls import path, re_path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^admin/filebrowser/', site.urls),
    re_path(r'^tinymce/', include('tinymce.urls')),
]
```

1. Add CSS & JS file - static > css/js - `github.css & highlight.pack.js`

2. Link to HTML file - templates > base > css.html/scripts.html -

   `<link rel="stylesheet" href="{% static 'css/github.css' %}">`

   `<script type="text/javascript" src="{% static 'js/highlight.pack.js' %}"></script>`

3. Collect Static Files - `python manage.py collectstatic`


### III. Create Product Model with Multiple Images <a href="" name="product"> - </a>

* product > models.py

```py
from tinymce import HTMLField
from django.utils.safestring import mark_safe


class Product(models.Model):
    STATUS = (
        ('Published', 'Published'),
        ('Draft', 'Draft'),
    )
    LABEL = (
        ('New', 'New'),
        ('Bestseller', 'Bestseller'),
        ('Trending', 'Trending'),
        ('Topselling', 'Topselling'),
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    keywords = models.CharField(max_length=255, blank=True)
    description = models.TextField(max_length=255, blank=True)
    image = models.ImageField(upload_to='product/%Y/%m/%d/', null=False)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount = models.IntegerField(default=0)
    minamount = models.IntegerField()
    detail = HTMLField()
    label = models.CharField(max_length=20, blank=True, choices=LABEL)
    slug = models.SlugField(null=False, unique=True)
    status = models.CharField(max_length=10, choices=STATUS, default='Draft')
    slider_product = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def image_tag(self):
        return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))

    image_tag.short_description = 'Image'

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'id': self.id, 'slug': self.slug})

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Images(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, blank=True)
    image = models.ImageField(blank=True, upload_to='product/image/%Y/%m/%d/')

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = 'images'

```

* product > admin.py

```py
class ProductImageInline(admin.TabularInline):
    model = Images
    extra = 3


class ProductAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'category', 'status', 'image_tag']
    search_fields = ['__str__', 'title', 'price']
    list_filter = ['category']
    readonly_fields = ('image_tag',)
    inlines = [ProductImageInline]
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 10

    class Meta:
        model = Product


admin.site.register(Product, ProductAdmin)


class ImagesAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    list_per_page = 10

    class Meta:
        model = Images


admin.site.register(Images, ImagesAdmin)

```

1. Run Command - `python manage.py makemigrations` & `python manage.py migrate`
2. Create some category & product - `127.0.0.1:8000/admin`


## 2. Show All Nested Category with Template Tag <a href="" name="category"> - </a>

1. Create files > home - templatetags > `__init__.py` & `ecommercetags.py`

* home > templatetags > ecommercetags.py

```python
from django import template
from product.models import Category

register = template.Library()

@register.simple_tag
def categorylist():
    return Category.objects.all()
```


* templates > partials > _navbar.html

```html
{% load mptt_tags %}

{% load ecommercetags %}

<div class="category-nav">
    <span class="category-header">Categories <i class="fa fa-list"></i></span>
    {% categorylist as category %}

    <ul class="category-list">
    {% recursetree category %}
        <li class="dropdown side-dropdown">
            <a href="" class="dropdown-toggle" {% if not node.is_leaf_node %}data-toggle="dropdown" aria-expanded="true" {% endif %}>
                {{ node.title }} 
                {% if not node.is_leaf_node %} <i class="fa fa-angle-right"></i> {% endif %}
            </a>
            <div class="custom-menu">
                {% if not node.is_leaf_node %}
                <ul class="list-links">
                    <h3 class="list-links-title" style="padding-bottom: 20px;">
                        All {{ node.title }}
                    </h3>
                    <a href="#">{{ children }}</a>
                </ul>
                {% endif %}
                <hr class="hidden-md hidden-lg">
            </div>
        </li>
    {% endrecursetree %}
        <li><a href="#">View All</a></li>
    </ul>
</div>
```


## 3. Show All Products <a href="" name="products"> - </a>

> - <a href="#h_products">I. Show Products In Homepage </a>

> - <a href="#c_products">II. Show Category Wize Products  </a>

### I. Show Products In Homepage <a href="" name="h_products"> - </a>

* home > views.py 

```python
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

```

* templates > home > product.html

```html
{% if products %}

{% for product in products %}
<div class="product product-single">
    <div class="product-thumb">
        <div class="product-label">
            {% if product.label %}
                <span>{{ product.label }}</span>
            {% endif %}
        </div>
        <button class="main-btn quick-view">
            <i class="fa fa-search-plus"></i> Quick view
        </button>
        <img src="{{ product.imageURL }}" height="300px" width="100%" alt="">
    </div>
    <div class="product-body">
        <h3 class="product-price">${{ product.price }}</h3>
        <div class="product-rating">
            <i class="fa fa-star"></i>
            <i class="fa fa-star"></i>
            <i class="fa fa-star"></i>
            <i class="fa fa-star"></i>
            <i class="fa fa-star-o empty"></i>
        </div>
        <h3 class="product-name">
            <a href="#">{{ product.title|truncatewords:10 }}</a>
        </h3>
        <div class="product-btns">
            <button class="main-btn icon-btn"><i class="fa fa-heart"></i></button>
            <button class="main-btn icon-btn"><i class="fa fa-exchange"></i></button>
            <button class="primary-btn add-to-cart"><i class="fa fa-shopping-cart"></i> Add to Cart</button>
        </div>
    </div>
</div>
{% endfor %}

{% else %}
    <h2>There are No Products</h2>
{% endif %}
```

### II. Show Category Wize Products <a href="" name="c_products"> - </a>

1. Create File > templates > product - `category.html`

* product > views.py 

```python
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

```

* blog > urls.py 

```python
from django.urls import path
from .import views

urlpatterns = [
    path('category/<str:id>/<slug:slug>/', views.categoryView, name="category"),
]

```

* templates > product > categoty.html

```html
{% if products %}

{% for product in products %}
<div class="col-md-4 col-sm-6 col-xs-6">
    <div class="product product-single">
        <div class="product-thumb">
            <div class="product-label">
            {% if product.label %}
                <span>{{ product.label }}</span>
            {% endif %}
            </div>
            <button class="main-btn quick-view">
                <i class="fa fa-search-plus"></i> Quick view
            </button>
            <img src="{{ product.imageURL }}" width="100%" height="300px" alt="">
        </div>
        <div class="product-body">
            <h3 class="product-price">${{ product.price }}</h3>
            <div class="product-rating">
                <i class="fa fa-star"></i>
                <i class="fa fa-star"></i>
                <i class="fa fa-star"></i>
                <i class="fa fa-star"></i>
                <i class="fa fa-star-o empty"></i>
            </div>
            <h2 class="product-name">
                <a href="#">{{ product.title|truncatewords:10 }}</a>
            </h2>
            <div class="product-btns">
                <button class="main-btn icon-btn"><i class="fa fa-heart"></i></button>
                <button class="main-btn icon-btn"><i class="fa fa-exchange"></i></button>
                <button class="primary-btn add-to-cart">
                    <i class="fa fa-shopping-cart"></i>Add to Cart
                </button>
            </div>
        </div>
    </div>
</div>
{% endfor %}

{% else %}
<h2>There are No Products</h2>
{% endif %}

```

1. Link to the Category page > partials > _navbar.html - `<a href="{{ node.get_absolute_url }}" </a>`






## Getting started

Steps:

1. Clone/pull/download this repository
2. Create a virtualenv with `virtualenv venv` and install dependencies with `pip install -r requirements.txt`
3. Configure your .env variables
4. Rename your project with `python manage.py rename <yourprojectname> <newprojectname>`
5. Collect all static files `python manage.py collectstatic`

This project includes:

1. 
2. 
2. 