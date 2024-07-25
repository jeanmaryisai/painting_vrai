from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='painting_list'),
    # path('', views.painting_list, name='painting_list'),
    # path('painting/<slug:slug>/', views.painting_detail, name='painting_detail'),
    # path('cart/', views.cart, name='cart'),
    # path('checkout/', views.checkout, name='checkout'),
    # path('order-complete/', views.order_complete, name='order_complete'),
    # path('add-to-cart/<int:painting_id>/', views.add_to_cart, name='add_to_cart'),
]
