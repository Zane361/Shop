from django.urls import path
from . import views


app_name = 'front'


urlpatterns = [
    path('', views.index, name='index'),
    # ---------- CATEGORY ----------
    path('category/<int:id>/', views.category_detail, name='category_detail'),
    # ---------- PRODUCT ----------
    path('product/<str:code>/', views.product_detail, name='product_detail'),
    path('product-list/', views.product_list, name='product_list'),
    path('random-product/', views.random_product, name='random_product'),
    # ---------- CART ----------
    path('carts/', views.carts, name='carts'),
    path('cart/<str:code>/', views.cart_detail, name='cart_detail'),
    path('cart/', views.cart_deactivate, name='cart_deactivate'),
    path('active/cart/', views.active_cart, name='active_cart'),
    path('add-to-cart/<str:code>', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('plus-minus/<int:id>/', views.plus_minus, name='plus_minus'),
    # ---------- WISHLIST ----------
    path('list-wishlist/', views.list_wishlist, name='list_wishlist'),
    path('add-to-wishlist/<str:code>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<str:code>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    # ---------- ORDER ----------
    path('list-orders/', views.list_orders, name='list_orders'),
    path('receive-order/<str:code>/', views.receive_order, name='receive_order'),
    path('reject-order/<str:code>/', views.reject_order, name='reject_order'),
]