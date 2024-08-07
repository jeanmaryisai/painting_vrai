from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('', views.home, name='painting_list'),
    path('shop/', views.PaintingListView.as_view(), name='painting_list'),
    path('painting/<slug:slug>/', views.painting_detail, name='painting'),
    path('cart/', views.cart, name='cart'),
    path('address/edit/<int:address_id>/', views.edit_address, name='edit_address'),
    path('address/add/', views.add_address, name='add_address'),
    path('checkout/', views.checkout, name='checkout'),
    # path('order-complete/', views.order_complete, name='order_complete'),
    path('add-to-cart/<int:painting_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:painting_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('custom_order/<uuid:uuid>/', views.custom_order, name='custom_order'),
    path('change-password/', views.change_password, name='change_password'),
    path('notifications/mark_all_as_read/', views.mark_all_messages_as_read, name='mark_all_messages_as_read'),
    path('address_inquiry/', views.address_inquiry, name='address_inquiry'),
    path('wishlist/add/<int:painting_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:painting_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/move-to-cart/<int:painting_id>/', views.move_to_cart, name='move_to_cart'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('assign_address/', views.assign_address, name='assign_address'),
    path('artist/', views.ArtistListView.as_view(), name='artist_list'),
    path('artist/<int:id>', views.artist_detail, name='artist'),

    path('redeem-promo-code/', views.redeem_promo_code_view, name='redeem_promo_code'),

]
