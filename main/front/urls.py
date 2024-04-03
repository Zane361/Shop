from django.urls import path
from . import views


app_name = 'front'


urlpatterns = [
    path('', views.index, name='index'),
    #
    path('product/<str:code>/', views.product_detail, name='product_detail'),
    path('category/<int:id>/', views.product_list, name='product_list'),
    #
    path('carts/', views.carts, name='carts'),
    path('cart/<str:code>/', views.cart_detail, name='cart_detail'),
    path('cart/', views.cart_deactivate, name='cart_deactivate'),
    path('active/cart/', views.active_cart, name='active_cart'),
    path('add-to-cart/<str:code>', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    #
    path('plus-minus/<int:id>/', views.plus_minus, name='plus_minus'),
    #
    path('list-wishlist/', views.list_wishlist, name='list_wishlist'),
    path('add-to-wishlist/<str:code>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<str:code>/', views.remove_from_wishlist, name='remove_from_wishlist'),
]