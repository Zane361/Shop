from django.shortcuts import redirect
from main import models

def staff_required(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff:
            result = func(request, *args, **kwargs)
        else:
            return redirect('front:index')
        return result
    return wrapper

def wishlist(request, code):
    product = models.Product.objects.get(code=code)
    try:
        models.WishList.objects.get(user=request.user, product=product)
        result = True
    except:
        result = False
    return result



            
