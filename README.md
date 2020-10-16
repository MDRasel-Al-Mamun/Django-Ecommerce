# Django E-Commerce Website

To Create a Full Ecommerce Website with Django

> - <a href="#model">1. Category & Product Model Setup </a>

> - <a href="#category">2. Show All Nested Category In Navbar </a>

> - <a href="#products">3. Show All Products </a>

> - <a href="#search">4. Search Functionality </a>

> - <a href="#detail">5. Product Details Page Dynamic </a>

> - <a href="#authentication">6. Authentication System </a>


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
    overview = HTMLField()
    product_description = HTMLField()
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
from django.utils import timezone
from django.shortcuts import render
from product.models import Product, Category, Images


def homeView(request):
    page = 'home'
    day = timezone.now() - timezone.timedelta(hours=24)
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


## 4. Search Functionality <a href="" name="search"> - </a>

> - <a href="#b_search">I. Basic Search Products </a>

> - <a href="#a_search">II. Auto Search with Ajax </a>

### I. Basic Search Products <a href="" name="b_search"> - </a>


1. Create Py File > home > `forms.py`
2. Create File > templates > home - `search.html`


* home > forms.py 

```python
from django import forms


class SearchForm(forms.Form):
    query = forms.CharField(max_length=100)
    catid = forms.IntegerField()
```

* home > views.py

```py
from .forms import SearchForm
from django.http import HttpResponseRedirect


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
```

* home > urls.py

```py
urlpatterns = [
    path('search/', views.searchView, name='search'),
]
```

* templates > partials > _header.html

```html
{% load mptt_tags %}

{% load ecommercetags %}

<div class="header-search">
    <form action="/search/" method="POST">
    {% csrf_token %}
        <input id="query" name="query" class="input search-input" value="{{query}}" type="text" placeholder="Enter your keyword">
    {% categorylist as category %}
        <select name="catid" class="input search-categories">
            <option value="0">All Categories</option>
        {% recursetree category %}
            {% if node.is_leaf_node %}
                <option value="{{ node.id }}">{{ node.title }}</option>
            {% endif %}
            {% if not node.is_leaf_node %}
                <optgroup label="{{ node.title }}">{{ children }}</optgroup>
            {% endif %}
        {% endrecursetree %}
        </select>
        <button type="submit" class="search-btn"><i class="fa fa-search"></i></button>
    </form>
</div>
```

* templates > home > search.html

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

### II. Auto Search with Ajax <a href="" name="a_search"> - </a>

1. Add CSS & JS file - static > css/js - `jquery-ui.min.css & jquery-ui.min.js`

2. Link to HTML file - templates > base > css.html/scripts.html -

   `<link rel="stylesheet" href="{% static 'css/jquery-ui.min.css' %}">`

   `<script type="text/javascript" src="{% static 'js/jquery-ui.min.js' %}"></script>`


* home > views.py 

```python
import json
from django.http import HttpResponse


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

```

* home > urls.py

```py
urlpatterns = [
    path('search_auto/', views.searchAuto, name='search_auto'),
]

```

* static > js > main.js

```js
 $(function () {
  $("#query").autocomplete({
   source: "/search_auto/",
   select: function (event, ui) {
    AutoCompleteSelectHandler(event, ui)
   },
   minLength: 2,
  });
 });

 function AutoCompleteSelectHandler(event, ui) {
  var selectedObj = ui.item;
 }
```

1. Must User This ID > templates > partials > _header.html- `<input id="query" name="query" class="input search-input" value="{{query}}" type="text" placeholder="Enter your keyword">`

## 5. Product Details Page Dynamic <a href="" name="detail"> - </a>

> - <a href="#p_details">I. Show Product Details </a>

> - <a href="#c_details">II. Product Comment System </a>

### I. Show Product Details <a href="" name="p_details"> - </a>

* product > views.py 

```py
def productDetail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug)
    images = Images.objects.filter(product=product)
    product_pick = Product.objects.filter(status='Published').order_by('?')[:4]
    context = {
        'product': product,
        'images': images,
        'product_pick': product_pick,
    }
    return render(request, 'product/product_detail.html', context)
```

* product > urls.py

```py
urlpatterns = [
    path('<str:id>/<slug:slug>', views.productDetail, name='product_detail'),
]
```

* templates > product > product_detail.html

```html
<div class="col-md-6">
    <div id="product-main-view">
        <div class="product-view">
            <img src="{{ product.imageURL }}" height="550px" alt="">
        </div>
        {% if images %}
        {% for image in images %}
        <div class="product-view">
            <img src="{{ image.image.url }}" height="550px" alt="">
        </div>
        {% endfor %}
        {% endif %}
    </div>

    <div id="product-view">
        <div class="product-view">
            <img src="{{ product.imageURL }}" width="120px" height="120px" alt="">
        </div>
        {% if images %}
        {% for image in images %}
        <div class="product-view">
            <img src="{{ image.image.url }}" width="120px" height="120px" alt="">
        </div>
        {% endfor %}
        {% endif %}
    </div>
</div>


<div class="col-md-6">
    <div class="product-body">
        <div class="product-label">
            {% if product.label %}
            <span>{{ product.label }}</span>
            {% endif %}
        </div>
        <h2 class="product-name">{{ product.title }}</h2>
        <h3 class="product-price">${{ product.price }}</h3>
        <div>
            <div class="product-rating">
                <i class="fa fa-star"></i>
                <i class="fa fa-star"></i>
                <i class="fa fa-star"></i>
                <i class="fa fa-star"></i>
                <i class="fa fa-star-o empty"></i>
            </div>
            <a href="#">3 Review(s) / Add Review</a>
        </div>
        <p><strong>Availability:</strong> In Stock</p>
        <p><strong>Brand:</strong> E-SHOP</p>
        <p>
            {{ product.overview|safe }}
        </p>
    </div>
</div>

<div class="col-md-12">
    <div class="product-tab">
        <ul class="tab-nav">
            <li class="active"><a data-toggle="tab" href="#tab1">Description</a></li>
            <li><a data-toggle="tab" href="#tab2">Details</a></li>
            <li><a data-toggle="tab" href="#tab3">Reviews (3)</a></li>
        </ul>
        <div class="tab-content">
            <div id="tab1" class="tab-pane fade in active">
                <p>{{ product.product_description|safe }}</p>
            </div>
            <div id="tab2" class="tab-pane fade in">
                {{ product.detail|safe }}
            </div>
        </div>
    </div>
</div>


{% for pick in product_pick %}
<div class="col-md-3 col-sm-6 col-xs-6">
    <div class="product product-single">
        <div class="product-thumb">
            <div class="product-label">
                {% if pick.label %}
                <span>{{ pick.label }}</span>
                {% endif %}
            </div>
            <a href="{{ pick.get_absolute_url }}" class="main-btn quick-view">
                <i class="fa fa-search-plus"></i> Quick view
            </a>
            <img src="{{ pick.imageURL }}" height="300px" width="100%" alt="">
        </div>
        <div class="product-body">
            <h3 class="product-price">${{ pick.price }}
            </h3>
            <div class="product-rating">
                <i class="fa fa-star"></i>
                <i class="fa fa-star"></i>
                <i class="fa fa-star"></i>
                <i class="fa fa-star"></i>
                <i class="fa fa-star-o empty"></i>
            </div>
            <h2 class="product-name">
                <a href="{{ pick.get_absolute_url }}">
                    {{ pick.title|truncatewords:10 }}
                </a>
            </h2>
            <div class="product-btns">
                <button class="main-btn icon-btn"><i class="fa fa-heart"></i></button>
                <button class="main-btn icon-btn"><i class="fa fa-exchange"></i></button>
                <button class="primary-btn add-to-cart">
                    <i class="fa fa-shopping-cart"></i> Add to Cart
                </button>
            </div>
        </div>
    </div>
</div>
{% endfor %}
```

1. Link To Product Details Page -`<a href="{{ product.get_absolute_url }}"></a>`

### II. Product Comment System <a href="" name="c_details"> - </a>


> - <a href="#m_comment">I. Comment Model & Form Setup </a>

> - <a href="#v_comment">II. Create Views & URL </a>

> - <a href="#f_comment">III. Show Comment Detail & Form Setup </a>

### I. Comment Model & Form Setup <a href="" name="m_comment"> - </a>

* product > models.py

```py
from django.contrib.auth.models import User
from django.forms import ModelForm


class Comment(models.Model):
    STATUS = (
        ('New', 'New'),
        ('True', 'True'),
        ('False', 'False'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200, blank=True)
    comment = models.CharField(max_length=400, blank=True)
    rate = models.IntegerField(default=1)
    ip = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
    class Meta:
        ordering = ['-id']


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['subject', 'comment', 'rate']

```

* product > admin.py

```py
class CommentAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'comment', 'status', 'create_at']
    list_filter = ['status']
    readonly_fields = ('__str__', 'comment', 'subject', 'ip', 'user', 'product', 'rate', 'id')

    class Meta:
        model = Comment


admin.site.register(Comment, CommentAdmin)
```
1. Run Command - `python manage.py makemigrations` & `python manage.py migrate`


### II. Create Views & URL <a href="" name="v_comment"> - </a>

* product > views.py

```py
def productDetail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug)
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
```

* product > urls.py

```py
urlpatterns = [
    path('addcomment/<str:id>/<slug:slug>/', views.addComment, name='addcomment'),
]

```

### III. Show Comment Detail & Form Setup <a href="" name="f_comment"> - </a>


* product > models.py

```py
class Product(models.Model):

    @property
    def avaregereview(self):
        reviews = Comment.objects.filter(product=self).aggregate(avarage=Avg('rate'))
        avg = 0
        if reviews["avarage"] is not None:
            avg = float(reviews["avarage"])
        return avg

    @property
    def countreview(self):
        reviews = Comment.objects.filter(product=self).aggregate(count=Count('id'))
        cnt = 0
        if reviews["count"] is not None:
            cnt = int(reviews["count"])
        return cnt
```

* templates > product > product_detail.html

1. Comment Form Setup In Template

```html
<form class="review-form" action="{% url 'addcomment' product.id product.slug %}" method="POST">
    {% csrf_token %}
    <div class="form-group">
        <input class="input" name="subject" type="text" placeholder="Your Subject" required />
    </div>
    <div class="form-group">
        <textarea class="input" name="comment" placeholder="Your review" required></textarea>
    </div>
    <div class="form-group">
        <div class="input-rating">
            <strong class="text-uppercase">Your Rating: </strong>
            <div class="stars">
                <input type="radio" id="star5" name="rate" value="5" />
                <label for="star5"></label>
                <input type="radio" id="star4" name="rate" value="4" />
                <label for="star4"></label>
                <input type="radio" id="star3" name="rate" value="3" />
                <label for="star3"></label>
                <input type="radio" id="star2" name="rate" value="2" />
                <label for="star2"></label>
                <input type="radio" id="star1" name="rate" value="1" />
                <label for="star1"></label>
            </div>
        </div>
    </div>
    
    {% if user.is_authenticated %}
        <button class="primary-btn">Submit</button>
    {% else %}
        <p>You must be Logged in to post a review</p>
    {% endif %}
    
</form>
```

2. Show Comment With Pagination In Template

```html
<ul class="tab-nav">
    <li><a data-toggle="tab" href="#tab3">Reviews ( {{ product.countreview }} )</a></li>
</ul>

<div class="product-reviews">

    {% for comment in  comment_page.object_list %}
    <div class="single-review">
        <div class="review-heading">
            <div>
                <a href="#">
                    <i class="fa fa-user-o"></i> {{ comment.user.username }}
                </a>
            </div>
            <div><a href="#">
                <i class="fa fa-clock-o"></i> {{ comment.create_at }}</a>
            </div>
            <div class="review-rating pull-right">
                <i class="fa fa-star {% if comment.rate < 1 %}-o empty {% endif %}"></i>
                <i class="fa fa-star {% if comment.rate < 2 %}-o empty {% endif %}"></i>
                <i class="fa fa-star {% if comment.rate < 3 %}-o empty {% endif %}"></i>
                <i class="fa fa-star {% if comment.rate < 4 %}-o empty {% endif %}"></i>
                <i class="fa fa-star{% if comment.rate < 5 %}-o empty {% endif %}"></i>
            </div>
        </div>
        <div class="review-body">
            <p> <b> {{ comment.subject }}</b> </p>
        </div>
        <div class="review-body">
            <p>{{ comment.comment }}</p>
        </div>
    </div>
    {% endfor %}
    <nav>
        <ul class="pagination">
            {% if prev_page_url %}
            <li>
                <a href="{{ prev_page_url }}" aria-label="Previous">
                    <span aria-hidden="true">&laquo;</span>
                </a>
            </li>
            {% endif %}
            {% for n in comment_page.paginator.page_range %}
            {% if comment_page.number == n %}
            <li class="active">
                <a href="?page={{ n }}">{{ n }}</a>
            </li>
            {% elif n > comment_page.number|add:-3 and n < comment_page.number|add:3 %}
            <li><a href="?page={{ n }}">{{ n }}</a></li>
            {% endif %}
            {% endfor %}
            {% if next_page_url %}
            <li>
                <a href="{{ next_page_url }}" aria-label="Next">
                    <span aria-hidden="true">&raquo;</span>
                </a>
            </li>
            {% endif %}
        </ul>
    </nav>
</div>
```

3. Show Comment Average In Template (home/product.html, home/search.html, product/category.html)

```html
<div class="product-rating">
    <i class="fa fa-star{% if product.avaregereview < 1%}-o empty{% endif%}"></i>
    <i class="fa fa-star{% if product.avaregereview < 2%}-o empty{% endif%}"></i>
    <i class="fa fa-star{% if product.avaregereview < 3%}-o empty{% endif%}"></i>
    <i class="fa fa-star{% if product.avaregereview < 4%}-o empty{% endif%}"></i>
    <i class="fa fa-star{% if product.avaregereview < 5%}-o empty{% endif%}"></i>
    {{ product.avaregereview }} / {{ product.countreview }}
</div>

```

## 6. Authentication System <a href="" name="authentication"> - </a>

> - <a href="#validition">I. Sign Up Form Validition </a>

> - <a href="#signup">II.  Create an account with email verification  </a>

> - <a href="#signin">III. Sign In & Sign Out Precess </a>

> - <a href="#reset">IV. Reset Password & Set New Password </a>


### I. Sign Up Form Validition <a href="" name="validition"> - </a>

> - <a href="#jquery"> 1. jQuery Form Validition </a>

> - <a href="#password"> 2. Password strength check with jQuery </a>

> - <a href="#username"> 3. Username Validition with JsonResponse </a>

> - <a href="#email"> 4 .Email Validition with JsonResponse </a>


### 1. jQuery Form Validition <a href="" name="jquery"> - </a>

1. Add JS file - static > js - `jquery.min.js & jquery.validate.min.js`

2. Link to HTML filr - templates > base > scripts.html -

    `<script type="text/javascript" src="{% static 'js/jquery.min.js' %}"></script>`

    `<script type="text/javascript" src="{% static 'js/jquery.validate.min.js' %}"></script>`


* authentication > views.py   

```python
from django.shortcuts import render
from django.views.generic import View

class SignUpView(View):
    def get(self, request):
        return render(request, 'authentication/signup.html')
```

* authentication > urls.py   

```python
from django.urls import path
from .views import *

urlpatterns = [
    path('sign_up/', SignUpView.as_view(), name="signup"),
]
```

* templates > authentication > signup.html   

```html
<form id="validationForm" class="clearfix" method="POST">
{% csrf_token %}
{% include 'partials/_messages.html' %}
    <div class="col-md-6 col-md-offset-3">
        <div class="billing-details">
            <div class="row">
                <div class="col-md-6">
                    <div class="form-group">
                        <input class="input" type="text" name="first_name" placeholder="First Name">
                    </div>  
                </div>
                <div class="col-md-6">
                    <div class="form-group">
                        <input class="input" type="text" name="last_name" placeholder="Last Name">
                    </div>
                </div>
            </div>
            <div class="form-group">
                <input class="input" type="text" name="username" placeholder="Username">
            </div>
            <div class="form-group">
                <input class="input" type="email" name="email" placeholder="Email">
            </div>
            <div class="form-group">
                <input class="input" id="password" type="password" name="password" placeholder="Password">
            </div>
            <div class="form-group">
                <input class="input" type="password" name="confirm_password" placeholder="Re-enter Password">
            </div>
            <div class="form-group">
                <div class="checkbox">
                    <label>
                        <input type="checkbox" id="agree" name="agree" value="agree" />Please agree to our policy
                    </label>
                </div>
            </div>
            <button class="primary-btn">Sign Up</button>
            <div style="padding-top: 10px;">
                <p class="">Already have an account?
                    <a class="text-danger" href="">Sign In</a>
                </p>
            </div>
            <hr>
            <div class="">
                <p class="">By clicking <em>Sign up</em> you agree to our
                    <a href="" class="text-danger" target="_blank">terms of service</a>
                </p>
            </div>
        </div>
    </div>
</form>
```

* static > js > main.js 

```javascript
$(document).ready(function () {
  $('#validationForm').validate({
    rules: {
      first_name: 'required',
      last_name: 'required',
      username: {
        required: true,
        minlength: 6,
      },
      l_username: 'required',
      password: {
        required: true,
        minlength: 6,
      },
      l_password: 'required',
      confirm_password: {
        required: true,
        equalTo: '#password',
      },
      email: {
        required: true,
        email: true,
      },
      agree: 'required',
    },
    messages: {
      first_name: 'Please enter your first name',
      last_name: 'Please enter your last name',
      username: {
        required: 'Please enter a username',
        minlength: 'Your username must consist of at least 6 characters',
      },
      l_username: 'Please enter a username',
      password: {
        required: 'Please provide a password',
        minlength: 'Your password must be at least 6 characters long',
      },
      l_password: 'Please provide a password',
      confirm_password: {
        required: 'Please provide a password',
        equalTo: 'Please enter the same password as above',
      },
      email: 'Please enter a valid email address',
      agree: 'Please accept our policy',
    },
    errorElement: 'em',
    errorPlacement: function (error, element) {
      error.addClass('help-block');

      if (element.prop('type') === 'checkbox') {
        error.insertAfter(element.parent('label'));
      } else {
        error.insertAfter(element);
      }
    },
    highlight: function (element, errorClass, validClass) {
      $(element)
        .parents('.form-group')
        .addClass('has-error')
        .removeClass('has-success');
    },
    unhighlight: function (element, errorClass, validClass) {
      $(element)
        .parents('.form-group')
        .addClass('has-success')
        .removeClass('has-error');
    },
  });
  if ($.fn.passwordStrength) {
    $('#password').passwordStrength({
      minimumChars: 6,
    });
  }
});
```

### 2. Password strength check with jQuery <a href="" name="password"> - </a>

1. Add JS file - static > js - `jquery.passwordstrength.js`

2. Link to HTML filr - templates > base > scripts.html -

    `<script type="text/javascript" src="{% static 'js/jquery.passwordstrength.js' %}"></script>`

* templates > authentication > signup.html   

```html
<div class="form-group">
    <input class="input" id="password" type="password" name="password" placeholder="Password">
</div>
```

* static > js > main.js 

```javascript
$(document).ready(function () {
    if ($.fn.passwordStrength) {
    $('#passwordField').passwordStrength({
      minimumChars: 6,
    });
  }
});
```

* static > css > style.css   

```css
#validationForm .progress {
  width: 100%;
  height: 5px;
  margin-top: 1rem;
  border-radius: 0;
  margin-bottom: 0.25rem;
}

#validationForm .password-score {
  font-size: 14px;
  font-weight: 700;
}

#validationForm .password-score span {
  font-size: 18px;
}

#validationForm .password-recommendation {
  font-size: 13px;
}

#validationForm .password-recommendation ul,
#validationForm .password-recommendation ol {
  padding-left: 0;
  list-style: none;
  text-decoration: none;
}

#validationForm #password-recommendation-heading {
  font-weight: 500;
  color: #0b0757;
  font-size: 14px;
  margin-bottom: 0.25rem;
}

#validationForm .progress {
  width: 100%;
  height: 5px;
  margin-top: 1rem;
  border-radius: 0;
  margin-bottom: 0.25rem;
}

#validationForm .password-score {
  font-size: 14px;
  font-weight: 700;
}

#validationForm .password-score span {
  font-size: 18px;
}

#validationForm .password-recommendation {
  font-size: 13px;
}

#validationForm .password-recommendation ul,
#validationForm .password-recommendation ol {
  padding-left: 0;
  list-style: none;
  text-decoration: none;
}

#validationForm #password-recommendation-heading {
  font-weight: 500;
  color: #0b0757;
  font-size: 14px;
  margin-bottom: 0.25rem;
}
```

### 3. Username Validition with JsonResponse <a href="" name="username"> - </a>

* authentication > views.py   

```python
import json
from django.http import JsonResponse
from django.contrib.auth.models import User


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'Username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'Sorry username is already taken, choose another one'}, status=409)
        return JsonResponse({'username_valid': True})
```

* authentication > urls.py   

```python
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('validate_username', csrf_exempt(UsernameValidationView.as_view()), name="validate_username"),
]
```

* templates > authentication >  signup.html   

```html
<div class="form-group">
    <input class="input" type="text" id="usernameField" name="username" placeholder="Username">
    <div class="usernameFeedBackArea has-error" style="display:none"></div>
</div>
```

* static > js > main.js   

```javascript
const usernameField = document.querySelector('#usernameField');
const feedBackArea = document.querySelector('.usernameFeedBackArea');


usernameField.addEventListener('keyup', (e) => {
  const usernameVal = e.target.value;
  usernameField.classList.remove('has-error');
  feedBackArea.style.display = 'none';
  if (usernameVal.length > 0) {
    fetch('/authentication/validate_username', {
      body: JSON.stringify({ username: usernameVal }),
      method: 'POST',
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.username_error) {
          usernameField.classList.add('has-error');
          feedBackArea.style.display = 'block';
          feedBackArea.innerHTML = `<p style="color:#a94442";>${data.username_error}</p>`;
        }
      });
  }
});
```

### 4 .Email Validition with JsonResponse <a href="" name="email"> - </a>

1. Command Prompt - `pip install validate-email`

* authentication > views.py   

```python
from validate_email import validate_email


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error': 'Please provide a valid email'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'Sorry, email is already used, choose another one '}, status=409)
        return JsonResponse({'email_valid': True})
```

* authentication > urls.py   

```python
from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
    path('validate_email', csrf_exempt(EmailValidationView.as_view()), name='validate_email'),
]
```

* templates > authentication >  signup.html   

```html
<div class="form-group">
    <input class="input" id="emailField" type="email" name="email" placeholder="Email">
    <div class="emailFeedBackArea has-error" style="display:none"></div>
</div>
```

* static > js > main.js   

```javascript
const emailField = document.querySelector('#emailField');
const emailFeedBackArea = document.querySelector('.emailFeedBackArea');


emailField.addEventListener('keyup', (e) => {
  const emailVal = e.target.value;
  emailField.classList.remove('has-error');
  emailFeedBackArea.style.display = 'none';
  if (emailVal.length > 0) {
    fetch('/authentication/validate_email', {
      body: JSON.stringify({ email: emailVal }),
      method: 'POST',
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.email_error) {
          emailField.classList.add('has-error');
          emailFeedBackArea.style.display = 'block';
          emailFeedBackArea.innerHTML = `<p style="color:#a94442";>${data.email_error}</p>`;
        }
      });
  }
});
```

### II.  Create an account with email verification <a href="" name="signup"> - </a>

1.Create Files > templates > authentication - `email.html` & `signin.html` | templates > partials - `_messages.html`

* ecommerce > settings > base.py

```python
from django.contrib import messages
from decouple import config

MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}

EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
```

* root > Create a file > .env 

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=abc@example.com
DEFAULT_FROM_EMAIL=abc@example.com
EMAIL_HOST_PASSWORD=*************
EMAIL_USE_TLS=True
EMAIL_PORT=587
```

* authentication > views.py 

```python
import threading
from django.contrib import messages
from django.core.mail import EmailMessage
from . utils import account_activation_token
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    def run(self):
        self.email.send(fail_silently=False)


class SignUpView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return render(request, 'authentication/signup.html')
    
    def post(self, request):
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'message': first_name,
            'values': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 8:
                    return render(request, 'authentication/signup.html', context)
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                user.is_active = False
                user.save()

                current_site = get_current_site(request)
                email_subject = 'Activate your account'
                email_body = render_to_string('authentication/email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })

                email = EmailMessage(
                    email_subject,
                    email_body,
                    'djangoprojectbd@gmail.com',
                    [email],
                )
                EmailThread(email).start()
                return render(request, 'authentication/signup.html', context)
        return render(request, 'authentication/signup.html', context)


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('signin'+'?message='+'User Already Activated')

            if user.is_active:
                return redirect('signin')
            user.is_active = True
            user.save()

            messages.success(request, 'Account Activated Successfully')
            return redirect('signin')

        except Exception as ex:
            pass

        return redirect('signin')
        
class SigninView(View):
    def get(self, request):
        return render(request, 'authentication/signin.html')
```

* authentication > urls.py 

```python
urlpatterns = [
    path('sign_in/', SigninView.as_view(), name="signin"),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name='activate'),
]
```

* authentication > Create file > (utils.py) 

```python
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import 

class AppTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (text_type(user.is_active) + text_type(user.pk) + text_type(timestamp))

account_activation_token = AppTokenGenerator()
```

* template > authentication > signup.html 

```html
<div class="row">
    {% if message %}
    <div class="col-md-6 col-md-offset-3">
        <div class="text-center">
            <h1><span>Congratulations! {{ message }}</span></h1>
            <h3 class="">Your Account Successfully Created</h3>
            <h6>To Active Your Account, A Confirmation Code has Send to Your Email Address</h6>
            <h3 class="">Please Go to Your Email</h3>
            <a href="https://mail.google.com/" target="_blank" class="primary-btn">
                Email Confiramation
            </a>
        </div>
    </div>
    {% else %}
    <form id="validationForm" class="clearfix" action="{% url 'signup' %}" method="POST">
    {% csrf_token %}
    {% include 'partials/_messages.html' %}
        <div class="col-md-6 col-md-offset-3">
            <div class="billing-details">
                <div class="section-title"><h3 class="title">Sign Up</h3></div>
            <div class="row">
                <div class="col-md-6">
                    <div class="form-group">
                        <input class="input" type="text" name="first_name" placeholder="First Name">
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="form-group">
                        <input class="input" type="text" name="last_name" placeholder="Last Name">
                    </div>
                </div>
            </div>
            <div class="form-group">
                <input class="input" type="text" id="usernameField" name="username" placeholder="Username">
                <div class="usernameFeedBackArea has-error" style="display:none"></div>
            </div>
            <div class="form-group">
                <input class="input" id="emailField" type="email" name="email" placeholder="Email">
                <div class="emailFeedBackArea has-error" style="display:none"></div>
            </div>
            <div class="form-group">
                <input class="input" id="password" type="password" name="password" placeholder="Password">
            </div>
            <div class="form-group">
                <input class="input" type="password" name="confirm_password" placeholder="Re-enter Password">
            </div>
            <div class="form-group">
                <div class="checkbox">
                    <label>
                        <input type="checkbox" id="agree" name="agree" value="agree" />Please agree to our policy
                    </label>
                </div>  
            </div>
            <button class="primary-btn">Sign Up</button>
            <div style="padding-top: 10px;">
                <p class="">Already have an account?
                    <a class="text-danger" href="{% url 'signin' %}">Sign In</a>
                </p>
            </div>
            <hr>
            <div class="">
                <p class="">By clicking <em>Sign up</em> you agree to our
                    <a href="" class="text-danger" target="_blank">terms of service</a>
                </p>    
            </div>
            </div>
        </div>
    </form>
    {% endif %}
</div>
```

* template > authentication > email.html 

```django
{% autoescape off%}

Hi {{user.username}},

Thanks to join with us.
Please click this link below to verify your account

http://{{domain}}{% url 'activate' uidb64=uid token=token %}

{% endautoescape %}
```

* template > partials > _messages.html 

```django
{% if messages %}
<div class="messages">
  {% for message in messages %}
  <div {% if message.tags %} class="alert alert-sm alert-{{ message.tags }}" {% endif %}>
    {{ message }}
  </div>
  {% endfor %}
</div>
{% endif %}
```

### III. Sign In & Sign Out Precess <a href="" name="signin"> - </a>

* templates > authentication > signin.html

```html

<form id="validationForm" class="clearfix" action="{% url 'signin' %}" method="POST">
{% csrf_token %}
{% include 'partials/_messages.html' %}
    <div class="col-md-6 col-md-offset-3">
        <div class="billing-details">
            <div class="section-title"><h3 class="title">Sign In</h3></div>
            <div class="form-group">
                <input class="input" type="text" id="username" name="l_username" placeholder="Username">
            </div>
            <div class="form-group">
                <input class="input" type="password" name="l_password" placeholder="Password">
            </div>
            <div class="form-group">
                <div class="checkbox">
                <label>
                    <input type="checkbox" value="agree" />Remember me
                </label>
                <a style="float: right;" class="text-danger" href="{% url 'reset_password' %}">Forgot password?</a>
                </div>
            </div>
            
            <button class="primary-btn">Sign In</button>
            <div style="padding-top: 10px;">
                <p class="">Not a member?
                    <a class="text-danger" href="{% url 'signup' %}">Sign Up</a>
                </p>
            </div>
        </div>
    </div>
</form>
```

* authentication > views.py

```python
from django.contrib import auth
from django.contrib.auth import logout


class SigninView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return render(request, 'authentication/signin.html')

    def post(self, request):

        context = {
            'values': request.POST
        }

        username = request.POST['l_username']
        password = request.POST['l_password']

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    return redirect('home')
                messages.error(
                    request, 'Account is not active, please check your email')
                return render(request, 'authentication/signin.html', context)
            messages.error(request, 'Invalid credentials, try again')
            return render(request, 'authentication/signin.html', context)

        return render(request, 'authentication/signin.html', context)


def signoutView(request):
    logout(request)
    messages.success(request, 'You are sign out successfully')
    return redirect('signin')
```

* authentication > urls.py

```python
urlpatterns = [
    path('sign_in/', SigninView.as_view(), name="signin"),
    path('sign_out/', signoutView, name="signout"),
]
```

*templates > partials > _header.html

```django
{% if user.is_authenticated %}
    <a href="{% url 'signout' %}" class="text-uppercase">Sign Out</a>
    <ul class="custom-menu">
        <li><a href="#"><i class="fa fa-user-o"></i> My Account</a></li>
        <li><a href="#"><i class="fa fa-heart-o"></i> My Wishlist</a></li>
        <li><a href="#"><i class="fa fa-exchange"></i> Compare</a></li>
        <li><a href="#"><i class="fa fa-check"></i> Checkout</a></li>
    </ul>
{% else %}
    <a href="{% url 'signin' %}" class="text-uppercase">Login</a> /
    <a href="{% url 'signup' %}" class="text-uppercase">Join</a>
{% endif %}
```

### IV. Reset Password & Set New Password <a href="" name="reset"> - </a>

1.Create Files > templates > authentication - `reset_password.html` & `new_password.html`

* templates > authentication > reset_password.html

```html
<div class="row">
{% if email %}
    <div class="col-md-6 col-md-offset-3">
        <div class="text-center">
            <h1><span>Hi ! there,</span></h1>
            <h3 class="">Password Reset Successfully</h3>
            <h6>To Confirm Your Raset Password, A Confirmation Code has Send to this</h6>
            <h5>{{ email }}</h5>
            <h3 class="">Please Go to Your Email</h3>
            <a href="https://mail.google.com/" target="_blank" class="primary-btn">
            Email Confiramation
            </a>
        </div>
    </div>
{% else %}
    <form id="validationForm" class="clearfix" action="{% url 'reset_password' %}" method="POST">
    {% csrf_token %}
    {% include 'partials/_messages.html' %}
        <div class="col-md-6 col-md-offset-3">
            <div class="billing-details">
                <div class="section-title"><h3 class="title">Reset Password </h3></div>
                <div class="form-group">
                    <input class="input" type="email" name="email" placeholder="Email">
                </div>
                <button class="primary-btn">Reset Password</button>
                <div style="padding-top: 10px;">
                    <p class="">Already have an account?
                        <a class="text-danger" href="{% url 'signin' %}">Sign In</a>
                    </p>
                </div>
            </div>
        </div>
    </form>
{% endif %}
</div>

```

* templates > authentication > new_password.html


```html
<form id="validationForm" class="clearfix" action="{% url 'reset_user_password' uidb64 token %}" method="POST">
{% csrf_token %}
{% include 'partials/_messages.html' %}
    <div class="col-md-6 col-md-offset-3">
        <div class="billing-details">
            <div class="section-title"><h3 class="title">Set New Password</h3></div>
            <div class="form-group">
                <input class="input" id="password" type="password" name="password" placeholder="Password">
            </div>
            <div class="form-group">
                <input class="input" type="password" name="confirm_password" placeholder="Re-enter Password">
            </div>
            <button class="primary-btn">Submit</button>
            <div style="padding-top: 10px;">
                <p class="">Not a member?
                    <a class="text-danger" href="{% url 'signup' %}">Sign Up</a>
                </p>
            </div>
        </div>
    </div>
</form>
```

* authentication > views.py

```python
from django.urls import reverse
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class RequestPasswordResetEmail(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return render(request, 'authentication/reset_password.html')

    def post(self, request):
        email = request.POST['email']
        context = {
            'email': email,
            'values': request.POST
        }
        if not User.objects.filter(email=email).exists():
            messages.error(request, 'Please enter your correct email address')
            return render(request, 'authentication/reset_password.html')

        user = User.objects.filter(email=email)
        current_site = get_current_site(request)

        if user.exists():
            email_contant = {
                'user': user[0],
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0]),
            }
            link = reverse('reset_user_password', kwargs={
                'uidb64': email_contant['uid'], 'token': email_contant['token']})

            email_subject = 'Password Reset Instructions'
            reset_url = 'http://'+current_site.domain+link

            email = EmailMessage(
                email_subject,
                'Hi there, Please click the link below to reset your password \n'+reset_url,
                'djangoprojectbd@gmail.com',
                [email],
            )
            EmailThread(email).start()
            return render(request, 'authentication/reset_password.html', context)

        return render(request, 'authentication/reset_password.html', context)


class CompletePasswordReset(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))

            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(
                    request, 'Password reset link is invalid, please request a new one')
                return redirect('reset_password')

        except DjangoUnicodeDecodeError as identifier:
            messages.success(request, 'Invalid link')
            return render(request, 'authentication/new_password.html')
        return render(request, 'authentication/new_password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }
        password = request.POST['password']

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()

            messages.success(request, 'Password reset success, you can sign in with new password')
            return redirect('signin')

        except DjangoUnicodeDecodeError as identifier:
            messages.error(request, 'Something went wrong')
            return render(request, 'authentication/new_password.html', context)

        return render(request, 'authentication/new_password.html', context)
```

* authentication > urls.py

```python
urlpatterns = [
    path('reset_password/', RequestPasswordResetEmail.as_view(), name="reset_password"),
    path('set_new_password/<uidb64>/<token>', CompletePasswordReset.as_view(), name='reset_user_password'),
]
```

* templates > authentication > signin.html

```django
<a href="{% url 'reset_password' %}">Forgot password?</a>
```

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