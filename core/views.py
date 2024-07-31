from django.shortcuts import render, get_object_or_404, redirect
from .models import Painting, Order, OrderItem, Review, Artist, Category, Tag
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from .forms import AddressForm

def address_inquiry(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))  # Redirect to the same page
    else:
        form = AddressForm()
    return render(request, 'address_form.html', {'form': form})

def home(request):
    return render(request, 'about.html')



def painting_list(request):

    categories = Category.objects.all()
    context={'categories': categories}
    paintings = Painting.objects.filter(show=True)
    try:
        query = request.GET.get('q')
        paintings = Painting.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(artist__name__icontains=query) |
                Q(category__name__icontains=query) |
                Q(tags__name__icontains=query),
                show=True
            ).distinct()
        context['query']=query
        
    except:
        pass
           

    paginator = Paginator(paintings, 15)  # Affiche 15 peintures par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context['context']=page_obj


    return render(request, 'products.html', context)



def painting_detail(request, slug):
    painting = get_object_or_404(Painting, slug=slug)
    reviews = Review.objects.filter(painting=painting)
    
    return render(request, 'product.html', {'obj': painting,'reviews':reviews})

@login_required
def add_to_cart(request, painting_id):
    painting = get_object_or_404(Painting, pk=painting_id)
    order, created = Order.objects.get_or_create(user=request.user, status='PENDING')
    order_item, created = OrderItem.objects.get_or_create(order=order, painting=painting)
    if not created:
        order_item.quantity += 1
    order_item.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def cart(request):
    order = get_object_or_404(Order, user=request.user, status='PENDING')
    return render(request, 'cart.html', {'order': order})

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



@login_required
def remove_single_item_from_cart(request, painting_id):
    order = Order.objects.filter(user=request.user, status='PENDING').first()
    painting = get_object_or_404(Painting, id=painting_id)
    order_item = get_object_or_404(OrderItem, order=order, painting=painting)

    if order_item.quantity > 1:
        order_item.quantity -= 1
        order_item.save()
    else:
        order_item.delete()

    return redirect('cart')  # Redirige vers la vue du panier

@login_required
def remove_from_cart(request, painting_id):
    order = Order.objects.filter(user=request.user, status='PENDING').first()
    painting = get_object_or_404(Painting, id=painting_id)
    order_item = get_object_or_404(OrderItem, order=order, painting=painting)

    order_item.delete()

    return redirect('cart')  # Redirige vers la vue du panier

@login_required
def clear_cart(request):
    order = Order.objects.filter(user=request.user, status='PENDING').first()
    order.orderitem_set.all().delete()
    
    return redirect('cart')  