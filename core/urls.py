from django.urls import path
from . import views

urlpatterns = [
    path('default-address/<int:address_id>/', views.set_default_address, name='default-address'),
    path('delete-address/<int:address_id>/', views.delete_address, name='delete-address'),
    
    
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('shop/', views.PaintingListView.as_view(), name='painting_list'),
    path('painting/<slug:slug>/', views.painting_detail, name='painting'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.payment, name='payment'),
  
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('payment/processing/', views.process_payment, name='process_payment'),
    path('webhook', views.stripe_webhook, name='stripe_webhook'),
    path('request-seller/', views.seller_request, name='seller_request'),
    


      # path('order-complete/', views.order_complete, name='order_complete'),
    path('add-to-cart/<int:painting_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:painting_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('remove_single_from_cart/<int:painting_id>/', views.remove_single_from_cart, name='remove_single_from_cart'),
    path('custom_order/<uuid:uuid>/', views.custom_order, name='custom_order'),
   
    


    path('address/edit/<int:address_id>/', views.edit_address, name='edit_address'),
    path('address/add/', views.add_address, name='add_address'),
    # path('address_inquiry/', views.address_inquiry, name='address_inquiry'),


    
    path('redeem-promo-code/', views.redeem_promo_code_view, name='redeem_promo_code'),


    path('wishlist/add/<int:painting_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:painting_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/move-to-cart/<int:painting_id>/', views.move_to_cart, name='move_to_cart'),
   

    path('account', views.account, name='account'),
   

    path('artist/', views.ArtistListView.as_view(), name='artist_list'),
    path('artist/<int:id>', views.artist_detail, name='artist'),

    # #PayPal IPN
    # path('paypal',include('paypal.standard.ipn.urls')),
    

]
