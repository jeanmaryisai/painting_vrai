from datetime import timezone
from django.db import models
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
# from colorfield.fields import ColorField




class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(default=1)
    users = models.ManyToManyField(User, through='PromoCodeUsage')

    def __str__(self):
        return self.code

class PromoCodeUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)


class Artist(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()
    birth_date = models.DateField(null=True, blank=True)
    profile=models.ImageField(upload_to='profile/')

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Painting(models.Model):
    title = models.CharField(max_length=200,unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='paintings/')
    created_at = models.DateTimeField(auto_now_add=True)
    tags=models.ManyToManyField(Tag)
    slug = models.SlugField(unique=True)
    show=models.BooleanField(default=True)
    # canvas_color = ColorField(default='#FFFFFF')
    fav=models.ManyToManyField(User,blank=True)

    def __str__(self):
        return self.title

    @property
    def isNew(self):
        return self.created_at >= timezone.now() - timedelta(days=90)


class Address(models.Model):
    STATUS_CHOICES = (
        ('CONFIRMED', 'Confirmed'),
        ('PENDING', 'Pending'),
        ('REFUSED', 'Refused'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    message = models.TextField(blank=True, null=True)
    shipping_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    default = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.address}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    payed_at = models.DateTimeField(null=True,blank=True)
    shipped_at = models.DateTimeField(null=True,blank=True)
    delivered_at = models.DateTimeField(null=True,blank=True)
    paintings = models.ManyToManyField(Painting, through='OrderItem')
    address=models.ForeignKey(Address,null=True,blank=True,on_delete=models.SET_NULL)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    promo_code = models.ForeignKey(PromoCode, null=True, blank=True, on_delete=models.SET_NULL)
    status_choices = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )
    status = models.CharField(max_length=20, choices=status_choices, default='PENDING')
    
    @property
    def discount(self):
        if self.promo_code:
            return (self.subtotal * self.promo_code.discount) / 100
        return 0
    
    @property
    def get_status_date(self):
        status_dates = {
            'PENDING': self.created_at,
            'PROCESSING': self.payed_at,
            'SHIPPED': self.shipped_at,
            'DELIVERED': self.delivered_at,
        }
        return status_dates.get(self.status, self.created_at)
    
    @property
    def subtotal(self):
        return sum(item.painting.price * item.quantity for item in self.orderitem_set.all())

    @property
    def shipping_address(self):
        if self.address.shipping_price: return self.address
        
        if not self.address:
            address= Address.objects.get(user=self.user, default=True)
            if address.exists:
                return address
        return False

    def total(self):
        if self.address.shipping_price:return self.shipping_address.shipping_price+self.subtotal-self.discount
        else: return self.subtotal-self.discount
        

    def __str__(self):
        return f'Order #{self.pk} - {self.user.username}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    painting = models.ForeignKey(Painting, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total(self):
        return self.quantity* self.painting.price
    def __str__(self):
        return f'{self.quantity} x {self.painting.title}'

class Review(models.Model):
    user = models.CharField(max_length=99)
    painting = models.ForeignKey(Painting, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user} on {self.painting.title}'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_message=models.BooleanField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

