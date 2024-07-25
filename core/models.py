from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
import uuid

class Artist(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Painting(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='paintings/')
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status_choices = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )
    status = models.CharField(max_length=20, choices=status_choices, default='PENDING')

    def __str__(self):
        return f'Order #{self.pk} - {self.user.username}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    painting = models.ForeignKey(Painting, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.painting.title}'

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    painting = models.ForeignKey(Painting, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.username} on {self.painting.title}'
