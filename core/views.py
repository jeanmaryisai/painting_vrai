from django.shortcuts import render, get_object_or_404, redirect
from .models import Painting, Order, OrderItem, Review
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'cart.html')

def painting_list(request):
    paintings = Painting.objects.all()
    return render(request, 'shop/painting_list.html', {'paintings': paintings})

def painting_detail(request, slug):
    painting = get_object_or_404(Painting, slug=slug)
    return render(request, 'shop/painting_detail.html', {'painting': painting})

@login_required
def add_to_cart(request, painting_id):
    painting = get_object_or_404(Painting, pk=painting_id)
    order, created = Order.objects.get_or_create(user=request.user, status='PENDING')
    order_item, created = OrderItem.objects.get_or_create(order=order, painting=painting)
    if not created:
        order_item.quantity += 1
    order_item.save()
    return redirect('shop:cart')

@login_required
def cart(request):
    order = get_object_or_404(Order, user=request.user, status='PENDING')
    return render(request, 'shop/cart.html', {'order': order})

@login_required
def checkout(request):
    order = get_object_or_404(Order, user=request.user, status='PENDING')
    if request.method == 'POST':
        # Process payment and complete the order
        order.status = 'PROCESSING'
        order.save()
        return redirect('shop:order_complete')
    return render(request, 'shop/checkout.html', {'order': order})

def order_complete(request):
    return render(request, 'shop/order_complete.html')
