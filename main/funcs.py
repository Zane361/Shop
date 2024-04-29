from django.shortcuts import redirect
from main import models

def staff_required(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            result = func(request, *args, **kwargs)
        else:
            return redirect('front:index')
        return result
    return wrapper

def wishlist_1(request, code):
    product = models.Product.objects.get(code=code)
    try:
        models.WishList.objects.get(user=request.user, product=product)
        result = True
    except:
        result = False
    return result

def wishlist_2(request, *args, **kwargs):
    if not args and not kwargs:
        products = models.Product.objects.all()
    elif kwargs and not args:
        products = models.Product.objects.filter(**kwargs)
    elif not kwargs and args:
        products = models.Product.objects.all().order_by(args[0])
    else:
        products = models.Product.objects.filter(**kwargs).order_by(args[0])
    resulted_products = []
    for product in products:
        data = models.WishList.objects.filter(product=product, user=request.user)
        if data:
            product.is_like = True 
        else:
            product.is_like = False
        resulted_products.append(product)
    return resulted_products



            
