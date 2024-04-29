from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from main import models
from main import funcs
import random




def index(request):
    try:
        products = funcs.wishlist_2(request)
        new_products = funcs.wishlist_2(request, '-date')
    except:
        products = models.Product.objects.all()
        new_products = models.Product.objects.all()
    categories = models.Category.objects.all()
    reviews = models.Review.objects.all().order_by('-mark')
    context = {
        'categories':categories,
        'products':products[:8],
        'new_products':new_products[:4],
        'reviews':reviews[:3]
        }
    return render(request, 'front/index.html',context)

# ---------- CATEGORY ----------

def category_detail(request, id):
    queryset = funcs.wishlist_2(request, category_id=id)
    categories = models.Category.objects.all()
    if request.method == 'GET':
        filtered_items = {}
        my_bool = False
        for key, value in request.GET.items():
            if value:
                if key == 'name':
                    key = 'name__icontains'
                elif key == 'price':
                    start = value.split(';')[0]
                    end = value.split(';')[1]
                    filtered_items['price__gte'] = start
                    filtered_items['price__lte'] = end
                    continue
                elif key == 'filter':
                    if value == '0':
                        continue
                    else:
                        my_bool = True
                        continue
                filtered_items[key] = value
        if my_bool:
            if request.GET.get('filter') == '1':
                queryset = funcs.wishlist_2(request, '-date', category_id=id, **filtered_items)
            elif request.GET.get('filter') == '2':
                queryset = funcs.wishlist_2(request, 'date', category_id=id, **filtered_items)
            elif request.GET.get('filter') == '3':
                queryset = funcs.wishlist_2(request, '-price', category_id=id, **filtered_items)
            elif request.GET.get('filter') == '4':
                queryset = funcs.wishlist_2(request, 'price', category_id=id, **filtered_items)
        else:
                queryset = funcs.wishlist_2(request, category_id=id, **filtered_items)            
    context = {
        'queryset':queryset,
        'categories':categories,
        }
    return render(request, 'front/category/detail.html',context)

# ---------- PRODUCT ----------

def product_detail(request, code):
    product = models.Product.objects.get(code=code)
    reviews = models.Review.objects.filter(product=product)
    images = models.ProductImg.objects.filter(product=product)
    mark = 0
    try:
        for i in reviews:
            mark += i.mark

        mark = int(mark/len(reviews)) if reviews else 0
    except:
        mark = 0
    if request.method =='POST':
        try:
            models.Review.objects.create(
                mark = int(request.POST.get('mark')),
                product = product,
                user = request.user,
                text = request.POST.get('text'),
            )
        except:
            raise ValueError('Xatolik!')
    context = {
        'product':product,
        'mark':mark,
        'rating':range(1,6),
        'images':images,
        'reviews':reviews,
        'result':funcs.wishlist_1(request, code),
    }
    return render(request, 'front/product/detail.html',context)

def product_list(request):
    queryset = funcs.wishlist_2(request)
    categories = models.Category.objects.all()
    if request.method == 'GET':
        filtered_items = {}
        my_bool = False
        for key, value in request.GET.items():
            if value:
                if key == 'name':
                    key = 'name__icontains'
                elif key == 'price':
                    start = value.split(';')[0]
                    end = value.split(';')[1]
                    filtered_items['price__gte'] = start
                    filtered_items['price__lte'] = end
                    continue
                elif key == 'filter':
                    if value == '0':
                        continue
                    else:
                        my_bool = True
                        continue
                filtered_items[key] = value
        if my_bool:
            if request.GET.get('filter') == '1':
                queryset = funcs.wishlist_2(request, '-date', **filtered_items)
            elif request.GET.get('filter') == '2':
                queryset = funcs.wishlist_2(request, 'date', **filtered_items)
            elif request.GET.get('filter') == '3':
                queryset = funcs.wishlist_2(request, '-price', **filtered_items)
            elif request.GET.get('filter') == '4':
                queryset = funcs.wishlist_2(request, 'price', **filtered_items)
        else:
                queryset = funcs.wishlist_2(request, **filtered_items)            
    context = {
        'queryset':queryset,
        'categories':categories,
        }
    return render(request, 'front/product/list.html', context)

def random_product(request):
    product = random.choice(models.Product.objects.all())
    return redirect('front:product_detail', product.code)

# ---------- CART ----------

@login_required(login_url='auth:login')
def carts(request):
    queryset = models.Cart.objects.filter(user=request.user, status=4)
    context = {'queryset':queryset}
    return render(request, 'front/carts/list.html', context)

@login_required(login_url='auth:login')
def active_cart(request):
    queryset , _ = models.Cart.objects.get_or_create(user=request.user, status=1)
    return redirect('front:cart_detail', queryset.code)

@login_required(login_url='auth:login')
def cart_detail(request, code):
    cart = models.Cart.objects.get(code=code)
    queryset = models.CartProduct.objects.filter(cart=cart)
    context = {
        'cart': cart,
        'queryset':queryset,
        }
        
    return render(request, 'front/carts/detail.html', context)

@login_required(login_url='auth:login')
def cart_deactivate(request):
    cart = models.Cart.objects.get(user=request.user, status=1)
    cart_products = models.CartProduct.objects.filter(cart=cart)
    print(cart_products)
    try:
        for product in cart_products:
            p = models.Product.objects.get(code=product.product.code)
            if p.quantity - product.count < 0:
                raise ValueError(f"{p.name} yetarli emas")
            else:
                p.quantity -= product.count
                p.save()
    except:
        raise ValueError("Qaysidir mahsulot yetarli emas")
    cart.status = 2
    cart.save()
    return redirect('front:index')

@login_required(login_url='auth:login')
def add_to_cart(request, code):
    cart = models.Cart.objects.filter(status=1, user=request.user)[0]
    product = models.Product.objects.filter(code=code)[0]
    try:
        cart_product = models.CartProduct.objects.filter(cart=cart, product=product)[0]
        cart_product.count += 1 
        cart_product.save()
    except:
        models.CartProduct.objects.create(
            product = product,
            cart = cart,
            count = 1
        )
    return redirect('front:index')

@login_required(login_url='auth:login')
def remove_from_cart(request, id):
    cart = models.Cart.objects.filter(status=1)[0]
    cart_product = models.CartProduct.objects.filter(id=id)[0]
    cart_product.delete()
    return redirect('front:cart_detail', cart.code)

@login_required(login_url='auth:login')
def plus_minus(request, id):
    product = models.CartProduct.objects.get(id=id)
    code = product.cart.code
    product.count = int(request.POST['count'])
    product.save()
    return redirect('front:cart_detail', code)

# ---------- WISHLIST ----------

@login_required(login_url='auth:login')
def list_wishlist(request):
    queryset = models.WishList.objects.filter(user=request.user)
    context = {
        "queryset":queryset
    }
    return render(request, 'front/wishlist/list.html', context)

@login_required(login_url='auth:login')
def add_to_wishlist(request, code):
    models.WishList.objects.create(
        user = request.user,
        product = models.Product.objects.filter(code=code)[0],
    )
    return redirect('front:list_wishlist')

@login_required(login_url='auth:login')
def remove_from_wishlist(request, code):
    try:
        product = models.WishList.objects.filter(user=request.user, product__code=code)[0]
        product.delete()
    except:
        return redirect('front:index')
    return redirect('front:list_wishlist') 

# ---------- ORDER ----------

@login_required(login_url='auth:login')
def list_orders(request):
    orders = models.Cart.objects.filter(user=request.user, status__in=[2,3])
    context = {
        'orders':orders
    }
    return render(request, 'front/orders/list.html', context)

@login_required(login_url='auth:login')
def receive_order(request, code):
    cart = models.Cart.objects.get(code=code)
    cart.status = 4
    cart.save()
    return redirect('front:list_orders')

@login_required(login_url='auth:login')
def reject_order(request, code):
    cart = models.Cart.objects.get(code=code)
    cart.status = 3
    cart.save()
    return redirect('front:list_orders')

