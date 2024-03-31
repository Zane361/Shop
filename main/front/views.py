from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from main import models

def index(request):
    categories = models.Category.objects.all()
    products = models.Product.objects.all()
    reviews = models.Review.objects.all()
    mark = 0
    for i in reviews:
        mark += i.mark
    
    mark = int(mark/len(reviews)) if reviews else 0
    context = {
        'categories':categories,
        'products':products,
        'rating':range(1,6),
        'mark':mark,
        }
    return render(request, 'front/index.html',context)

def product_detail(request,code):
    product = models.Product.objects.get(code=code)
    reviews = models.Review.objects.filter(product=product)
    images = models.ProductImg.objects.filter(product=product)
    mark = 0

    for i in reviews:
        mark += i.mark

    mark = int(mark/len(reviews)) if reviews else 0
    context = {
        'product':product,
        'mark':mark,
        'rating':range(1,6),
        'images':images,
        'reviews':reviews,
    }
    return render(request, 'front/product/detail.html',context)

def product_list(request,id):
    queryset = models.Product.objects.filter(category_id=id)
    categories = models.Category.objects.all()
    context = {
        'queryset':queryset,
        'categories':categories,
        }
    return render(request, 'front/category/product_list.html',context)


@login_required(login_url='auth:login')
def carts(request):
    queryset = models.Cart.objects.filter(user=request.user, is_active=False)
    context = {'queryset':queryset}
    return render(request, 'front/carts/list.html', context)


@login_required(login_url='auth:login')
def active_cart(request):
    queryset , _ = models.Cart.objects.get_or_create(user=request.user, is_active=True)
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
    cart = models.Cart.objects.get(user=request.user, is_active=True)
    cart.is_active = False
    cart.save()
    return redirect('front:index')

def add_to_cart(request, code):
    cart = models.Cart.objects.filter(is_active=True)[0]
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

def remove_from_cart(request, id):
    cart = models.Cart.objects.filter(is_active=True)[0]
    cart_product = models.CartProduct.objects.filter(id=id)[0]
    cart_product.delete()
    return redirect('front:cart_detail', cart.code)

def plus_minus(request, id):
    product = models.CartProduct.objects.get(id=id)
    code = product.cart.code
    product.count = int(request.POST['count'])
    product.save()
    return redirect('front:cart_detail', code)