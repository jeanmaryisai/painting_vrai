from .models import Painting, Order, OrderItem, Review, PromoCode, PromoCodeUsage, Category,Artist, Address,Notification
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect,JsonResponse
from .forms import AddAddressForm, AddressForm
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.views.generic import ListView


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

def home(request,id):
    return render(request, 'about.html')



class PaintingListView(ListView):
    model = Painting
    template_name = 'products.html'
    context_object_name = 'paintings'
    paginate_by = 15  # Number of items per page
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['query'] = self.request.GET.get('q')
        return context
    
    def get_queryset(self):
        queryset = Painting.objects.filter(show=True)
        query = self.request.GET.get('q')
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(artist__name__icontains=query) |
                Q(category__name__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()
        
        return queryset
    
class ArtistListView(ListView):
    model = Artist
    template_name = 'artists.html'
    context_object_name = 'artists'
    paginate_by = 15  # Number of items per page
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        return context
    
    def get_queryset(self):
        queryset = Artist.objects.all()
        query = self.request.GET.get('q')
        
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(bio__icontains=query) |
                Q(birth_date__icontains=query) 
            ).distinct()
        
        return queryset

def artist_detail(request, id):
    artist = get_object_or_404(Artist, id=id)
    paintings = artist.painting_set.all()

    paginator = Paginator(paintings, 20)  # Show 20 paintings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    page_obj.end_index

    return render(request, 'artist.html', {'obj': artist, 'page_obj': page_obj})


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
        order.status = 'PROCESSING'
        order.save()
        messages.success(request,'Your order have been place successfully')
        return redirect('account')
    
    
    addresses=Address.objects.filter(user=request.user,shipping_price__isNull=False,status= 'Confirmed')
    if not addresses.exists:
        messages.error(request, 'You do not have a confirmed Address please add an Address or if you have already added one, please wait for the administrator to confirm it')
        return redirect('account')
    if not order.address:
        x=get_object_or_404(Address, user=request.user, default=True)
    else:
        x=order.address
    context={'order': order,'addresses':addresses.exclude(id=x.id),'x':x}
    return render(request, 'checkout.html', context)

@login_required
def remove_single_from_cart(request, painting_id):
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

@login_required
def account(request):

    if request.method == 'POST':
        if request.POST.get('assign_address'):
            address_id = request.POST.get('assign_address')
            order = Order.objects.get(user=request.user, status='PENDING')
            address = get_object_or_404(Address, id=address_id, user=request.user)
            if not address.state == 'CONFIRMED':
                messages.error(request, 'You can only assign addresses that are already Confirmed')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            order.address = address
            order.save()                
            messages.info(request,'Your new address has been set for the current order')       
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))



    msj=Notification.objects.filter(user=request.user,is_message=True)
    context={
        'addresses':Address.objects.filter(user=request.user).order_by('-default'),
        'Orders':Order.objects.filter(user=request.user).order_by('-created_at'),
        'active_order': Order.objects.get(user=request.user, status='PENDING'),
        'messages2':msj,
        'wishlist': Painting.objects.filter(fav__id=request.user.id),
        'form':PasswordChangeForm(request.user)

    }

    if msj.filter(is_read=False).exists:
        context['newMsj']=True


    return render(request,'account.html',context)
      

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if address.default:
        messages.error(request, "Cannot delete the default address. Set another Adress to default first")
    else:
        address.delete()
        messages.success(request, "Address deleted successfully.")
    return redirect('account')

@login_required
def set_default_address(request, address_id):

    address = get_object_or_404(Address, id=address_id, user=request.user)
    if address.default:
        messages.error(request, "This address is already the default address.")
    else:
        request.user.addresses.update(default=False)
        address.default = True
        address.save()
        messages.success(request, "Default address set successfully.")
    return redirect('account')

@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)

    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            print('valid')
            if form.cleaned_data['default']:
                # Set all other addresses as non-default
                Address.objects.filter(user=request.user, save_as_default=True).update(default=False)
            form.save()
            messages.success(request, "Address updated successfully.")
        else:
            print('not valid')
    return redirect('account')

@login_required
def add_address(request):
    if request.method == "POST":
        form = AddAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if address.default:
                Address.objects.filter(user=request.user, default=True).update(default=False)
            address.save()

            # TODO:Sent email

            messages.success(request, "Address added successfully.")
            return redirect('account')  # Adjust this to the appropriate view
    else:
        form = AddAddressForm()

    return render(request, 'add_address.html', {'form': form})

@login_required
def custom_order(request,uuid):
    order = get_object_or_404(Order, uuid=uuid )
    if order.status=='PENDING':
        return redirect('cart')
    return render(request, 'cart.html', {'order': order,'old':True})

@login_required
def mark_all_messages_as_read(request):
    if request.method == 'POST':
        messages = Notification.objects.filter(user=request.user, is_message=True, is_read=False)
        messages.update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important, to update the session with the new password
            messages.success(request, 'Your password was successfully updated!')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the error below.')
    return redirect('account')


@login_required
def add_to_wishlist(request, painting_id):
    painting = get_object_or_404(Painting, id=painting_id)
    if request.user not in painting.fav.all():
        painting.fav.add(request.user)
        messages.success(request, f'the painting {painting.title} has been added to your wishlist.')
    else:
        messages.error(request, f'{painting.title} has already been added to your wishlist.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def remove_from_wishlist(request, painting_id):
    painting = get_object_or_404(Painting, id=painting_id)
    request.user.favorite_paintings.remove(painting)
    messages.success(request, f'{painting.title} has been removed from your wishlist.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def move_to_cart(request, painting_id):
    painting = get_object_or_404(Painting, id=painting_id)
    request.user.favorite_paintings.remove(painting)
    
    order, created = Order.objects.get_or_create(user=request.user, status='PENDING')
    order_item, created = OrderItem.objects.get_or_create(order=order, painting=painting)
    if not created:
        order_item.quantity += 1
        order_item.save()
    
    messages.success(request, f'{painting.title} has been moved to your cart.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def redeem_promo_code_view(request):
    if request.method == 'POST':
        promo_code = request.POST.get('promo_code')
        order = Order.objects.get(user=request.user, status='PENDING')  # or however you get the current order

        try:
            code = PromoCode.objects.get(code=promo_code, active=True)
            if PromoCodeUsage.objects.filter(promo_code=code, user=request.user).count() < code.usage_limit:
                PromoCodeUsage.objects.create(promo_code=code, user=request.user)
                order.promo_code = code
                order.save()
                messages.success(request, f'Promo code {promo_code} applied successfully!')
            else:
                messages.error(request, 'You have reached the usage limit for this promo code.')
        except PromoCode.DoesNotExist:
            messages.error(request, 'Invalid promo code.')

    return redirect('checkout')


