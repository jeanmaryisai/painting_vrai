from .models import Painting, Order, OrderItem, Review, PromoCode,Testemonial, Faq,PromoCodeUsage, Category,Artist, Address,Notification
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from .forms import AddAddressForm, AddressForm
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import ListView
from django.contrib.auth.forms import PasswordChangeForm
from django.conf import settings 
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.contrib.auth.models import User
import json
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactRequestForm,SellerRequestForm


def seller_request(request):
    if request.method == 'POST':
        form = SellerRequestForm(request.POST)
        if form.is_valid():
            # Get cleaned form data
            full_name = form.cleaned_data['fullName']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            business_name = form.cleaned_data['businessName']
            country = form.cleaned_data['country']
            description = form.cleaned_data.get('description', '')
            message = form.cleaned_data.get('message', '')
            website = form.cleaned_data.get('website', '')
            seller_request = form.save()

            # Prepare email content
            subject = "New Seller Request"
            email_message = f"""
            A new seller request has been submitted on your site.

            Full Name: {full_name}
            Email: {email}
            Phone: {phone}
            Business Name: {business_name}
            Country: {country}
            Business Description: {description}
            Message: {message}
            Website: {website}
            """

            # Send email to site owner
            send_mail(
                subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,  # From email
                [settings.CONTACT_EMAIL],  # To email
                fail_silently=False,
            )

            # Optionally, send a confirmation email to the user (the form submitter)
            send_mail(
                "Thank you for your request",
                "Thank you for your interest in becoming a seller on our platform. We will review your request and get back to you shortly.",
                settings.DEFAULT_FROM_EMAIL,  # From email
                [email],  # To email
                fail_silently=False,
            )
            
            # Show success message and redirect
            messages.success(request, 'Your request has been submitted successfully!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))  # Redirect to a relevant page, like home or a confirmation page

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def contact(request):
    if request.method == 'POST':
        form = ContactRequestForm(request.POST)
        if form.is_valid():
            contact_request = form.save()

            # Send a confirmation email
            send_mail(
                subject=f"New Contact Request from {contact_request.name}",
                message=(
                    f"Name: {contact_request.name}\n"
                    f"Email: {contact_request.email}\n"
                    f"Phone: {contact_request.phone}\n\n"
                    f"Message:\n{contact_request.message}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
            )

            # Redirect to a thank you page or show a success message
            messages.success(request, 'Thank you for contacting us. We will respond shortly.')
            return redirect('contact')
    else:
        form = ContactRequestForm()

    return render(request, 'contact.html', {'form': form})

def about(request):
    return render(request, 'about.html',{'faq': Faq.objects.filter(show=True)})

def home(request):
    return render(request, 'index.html',{'testimonies': Testemonial.objects.all()})






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
    order,created = Order.objects.get_or_create(user=request.user, status='PENDING')

    return render(request, 'cart.html', {'order': order,
                                         'addresses':Address.objects.filter(user=request.user,status='CONFIRMED').order_by('-default'),})
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
    painting.fav.remove(request.user)  
    messages.success(request,f'The painting {painting.title} has been removed from your wishlist')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def move_to_cart(request, painting_id):
    painting = get_object_or_404(Painting, id=painting_id)
    painting.fav.remove(request.user)  

    messages.success(request,f'The painting {painting.title} has been removed from your wishlist')

    return add_to_cart(request,painting.id)
    

@login_required
def redeem_promo_code_view(request):
    if request.POST.get('promo_code') and (request.POST.get('promo_code')!= ""):
        order = Order.objects.get(user=request.user, status='PENDING')
        promo_code = request.POST.get('promo_code')
        try:
            code = PromoCode.objects.get(code=promo_code, active=True)
            if PromoCodeUsage.objects.filter(promo_code=code, user=request.user).count() < code.usage_limit:
                PromoCodeUsage.objects.create(promo_code=code, user=request.user)
                order.promo_code = code
                order.save()
                messages.success(request, f'Promo code {promo_code} applied successfully!')
            else:
                messages.error(request, 'You have reached the usage limit for this promo code.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        except PromoCode.DoesNotExist:
            messages.error(request, 'Invalid promo code.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    



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
        'active_order': Order.objects.get_or_create(user=request.user, status='PENDING'),
        'messages2':msj,
        'wishlist': Painting.objects.filter(fav__id=request.user.id),
        'p_form':PasswordChangeForm(request.user)
        # ,'u_form': UserUpdateForm(request.user)

    }

    if msj.filter(is_read=False).exists:
        context['newMsj']=True


    return render(request,'account.html',context)
@login_required
def custom_order(request,uuid):
    order = get_object_or_404(Order, uuid=uuid )
    if order.status=='PENDING':
        return redirect('cart')
    return render(request, 'cart.html', {'order': order,'old':True})
    
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

            # TODO:Sent email to the customer and the admin about the new address

            messages.success(request, "Address added successfully.")
            return redirect('account')  # Adjust this to the appropriate view
    else:
        form = AddAddressForm()

    return render(request, 'add_address.html', {'form': form})




@login_required
def checkout(request):
    if request.method == 'POST':
        order=get_object_or_404(Order, user=request.user, status='PENDING')
        if order.orderitem_set.count() == 0:
            messages.error(request, 'Your cart is empty. Please add some items')
            return redirect('painting_list')
        address=get_object_or_404(Address, id=request.POST.get('address'))
        if address.status != 'CONFIRMED':
                messages.error(request, 'Invalid Address. Please select a confirmed address')
                return redirect('cart')
        
        
        redeem_promo_code_view(request)
        order.address = address
        order.save()

        # # Create a paypal form
        # paypal_dict = {
        #     'business': settings.PAYPAL_RECEIVER_EMAIL,
        #     'amount': order.total,
        #     'item_name': 'Art Shop',
        #     'invoice': str(order.uuid),
        #     'currency_code': 'CAD',
        #     'no_shipping': '2',
        #     'return': request.build_absolute_uri(reverse('cart')),
        #     'cancel_return': request.build_absolute_uri(reverse('cart')),
        #     'notify_url': request.build_absolute_uri(reverse('paypal-ipn')),
        # }

        # form = ExtPayPalPaymentsForm(initial=paypal_dict)


        return render(request, 'checkout.html', {'order': order,
                                                #  'form': form,
                                                 'addresses':Address.objects.filter(user=request.user,status='CONFIRMED').order_by('-default').exclude(id=order.address.id)})
    else:
        return redirect('cart')


@login_required
def payment(request):
    if  request.method == 'POST':
        order = get_object_or_404(Order, user=request.user, status='PENDING')
        if order.orderitem_set.count() == 0:
            messages.error(request, 'Your cart is empty. Please add some items')
            return redirect('painting_list')
        if order.address.status != 'CONFIRMED':
                messages.error(request, 'Invalid Address. Please select a confirmed address')
                return redirect('cart')


        YOUR_DOMAIN='http://127.0.0.1:8000'
        stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
        try:
            
            line_items = []
            for item in order.orderitem_set.all():
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(item.painting.price * 100),  # Stripe expects amount in cents
                        'product_data': {
                            'name': item.painting.title,
                            # 'images': [item.painting.image.url],  # Assuming `image` is a URL field
                        },
                    },
                    'quantity': item.quantity,
                })
            line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(order.shipping_address.shipping_price * 100),  # Stripe expects amount in cents
                        'product_data': {
                            'name': 'Shipping Address',
                            # 'images': [item.painting.image.url],  # Assuming `image` is a URL field
                        },
                    },
                    'quantity': 1,
                })
            checkout_session = stripe.checkout.Session.create(
                  payment_intent_data={
                      'metadata':{
                    'order_uuid': order.uuid,
                    'user_email': request.user.email,
                 },
                 },
                line_items=line_items,
                customer_email=request.user.email,
                # saved_payment_method_options={"payment_method_save": "enabled"},
                mode='payment',
               
                consent_collection={"terms_of_service": "required"},
                custom_text={
                    "terms_of_service_acceptance": {
                    "message": "I agree to the [Terms of Service](https://example.com/terms)",
                    },
                },
                # automatic_tax={"enabled": True},
                # ui_mode="embedded",
                
                success_url=YOUR_DOMAIN+'/payment/processing/',
                cancel_url=YOUR_DOMAIN+'/payment/cancel/',
            )
        except Exception as e:
            print(e)  # Log the error for debugging
            messages.error(request,e)
            return redirect('cart')

        return redirect(checkout_session.url, code=303)

    else:
        return redirect('cart')
@login_required
def payment_cancel(request):
    messages.error(request,"Your transaction has been cancelled.")
    return redirect('account')



@login_required
def process_payment(request):
    messages.success(request,"Your transaction is in progress.")
    return redirect('account')

@csrf_exempt
def stripe_webhook(request):
  stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
  payload = request.body
  event = None

  try:
    event = stripe.Event.construct_from(
      json.loads(payload), stripe.api_key
    )
  except ValueError as e:
    messages.error(request, f'Invalid payload: {e}')
    # Invalid payload
    return HttpResponse(status=400)

  # Handle the event
  if event.type == 'payment_intent.succeeded':
    payment_intent = event.data.object 
    user= get_object_or_404(User, email =payment_intent['metadata']['user_email'])
    order = get_object_or_404(Order, uuid =payment_intent['metadata']['order_uuid'], status='PENDING', user=user)
    total=order.total()*100
    
    if order.orderitem_set.count() == 0:
            messages.error(request, 'There was a probleme in the process of your order please contact the enterprise directly, your seems have paid for an empty cart')
            messages.error(request, 'Your transaction has been cancelled. Your order has been flagged as Problematic')
            order.status = 'PROBLEMATIC'
            print(1)
    elif order.address.status != 'CONFIRMED':
        messages.error(request, 'There was a probleme in the process of your order please contact the enterprise directly, your seems have paid for an order with no confirmed address')
        messages.error(request, 'Your transaction has been cancelled. Your order has been flagged as Problematic')
        order.status = 'PROBLEMATIC'
        print(2)
    
    elif int(payment_intent['amount']) != int(total):
        messages.error(request, 'There was a probleme in the process of your order please contact the enterprise directly, there was a problem regarding the amount paid')
        messages.error(request, 'Your transaction has been cancelled. Your order has been flagged as Problematic')
        order.status = 'PROBLEMATIC'
        print(3)
    else:
        order.status = 'PROCESSING'
        print(order.total(), payment_intent['amount'])
        messages.success(request, 'Your transaction has been completed successfully. You will receive an email confirmation shortly.')
        Order.objects.create(user=user,status='PENDING') 
        print(4)
    order.save()
    print(payment_intent)
  elif event.type == 'payment_method.attached':
    payment_method = event.data.object # contains a stripe.PaymentMethod
    messages.error(request,'PaymentMethod was attached to a Customer!')
  # ... handle other event types
  else:
    print('Unhandled event type {}'.format(event.type))

  return HttpResponse(status=200)


