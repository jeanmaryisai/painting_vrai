from datetime import timezone
from django.db import models
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill, ResizeToFit
from imagekit.models import ImageSpecField
from imagekit.processors import SmartResize, ResizeToFill, ResizeToFit





class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.code
    


class Artist(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()
    birth_date = models.DateField(null=True, blank=True)
    profile=ProcessedImageField(upload_to='profiles/', processors=[ResizeToFit(1500, 1500)], format='WEBP', options={'quality': 95})
    small = ImageSpecField(source='profile',
                           processors=[ResizeToFit(500, 500)],
                           format='WEBP',
                           options={'quality': 90})

    # WebP version
    medium = ImageSpecField(source='profile',
                          processors=[ResizeToFit(500, 500)],
                          format='WEBP',
                          options={'quality': 85})
    loading = ImageSpecField(source='profile',
                          processors=[ResizeToFit(20, 20)],
                          format='WEBP',
                          options={'quality': 55})
    

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
    created_at = models.DateTimeField(auto_now_add=True)
    tags=models.ManyToManyField(Tag)
    slug = models.SlugField(unique=True)
    show=models.BooleanField(default=True)
    # canvas_color = ColorField(default='#FFFFFF')
    fav=models.ManyToManyField(User,blank=True)
    # img=models.OneToOneField(Image, on_delete=models.CASCADE,null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def isNew(self):
        return self.created_at >= timezone.now() - timedelta(days=90)

class Image(models.Model):
    original_image = ProcessedImageField(upload_to='paintings/', processors=[ResizeToFit(1500, 1500)], format='WEBP', options={'quality': 95})
    painting=models.OneToOneField(Painting,null=True, blank=True,on_delete=models.CASCADE,related_name='painting')
    # Large size (e.g., 1200x1200 pixels)
    thumbnail=ImageSpecField(
        source='original_image',
        processors=[ResizeToFill(150, 150)],
        format='WEBP',
        options={'quality': 60}
    )
    small = ImageSpecField(source='original_image',
                           processors=[ResizeToFit(300, 300)],
                           format='WEBP',
                           options={'quality': 60})

    # WebP version
    medium = ImageSpecField(source='original_image',
                          processors=[ResizeToFit(500, 500)],
                          format='WEBP',
                          options={'quality': 80})
    
    loading=ImageSpecField(source='original_image',
                          processors=[ResizeToFit(20, 20)],
                          format='WEBP',
                          options={'quality': 40})

    def __str__(self):
        return self.original_image.name
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
    default = models.BooleanField(default=False, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.address}"

    def clean(self):
        # Call the parent clean method to ensure built-in validations are respected
        super().clean()

        # Example 2: Ensure shipping price is positive if set
        if self.shipping_price is not None and self.shipping_price <= 0:
            raise ValidationError(_('Shipping price must be a positive number.'))
        
        if self.status == 'CONFIRMED' and self.shipping_price is None:
            raise ValidationError(_('Shipping price must be provided for addresses marked as CONFIRMED.'))

        # Example 3: Ensure that at least one address field is provided
        if not self.address and not self.address2:
            raise ValidationError(_('At least one address field must be provided.'))

        # Example 4: Ensure that no two addresses for the same user are set as default
        if self.default:
            existing_defaults = Address.objects.filter(user=self.user, default=True).exclude(pk=self.pk)
            if existing_defaults.exists():
                raise ValidationError(_('Only one address can be set as default per user.'))

        # Example 5: Custom validation for zip code length based on country
        if self.country == "USA" and len(self.zip_code) != 5:
            raise ValidationError(_('In the USA, ZIP code must be exactly 5 digits.'))

        # Example 6: Ensure the status is not REFUSED if it’s marked as the default address
        if self.default and self.status == 'REFUSED':
            raise ValidationError(_('Default address cannot have a status of REFUSED.'))


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
        ('REFUNDED', 'Refunded'),
        ('PROBLEMATIC', 'Problematic'),
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
        if not self.address:
            return Address.objects.get(user=self.user, default=True)
           
        if self.address.shipping_price: return self.address
        

        return False

    def total(self):
        if self.subtotal == 0: return 0
        try:return self.shipping_address.shipping_price+self.subtotal-self.discount
        except: return self.subtotal-self.discount
        

    def __str__(self):
        return f'Order #{self.pk} - {self.user.username}'
    
    # def save(self, *args, **kwargs):
    #     # Automatically set the dates based on the status
    #     if self.status == 'PROCESSING' and not self.payed_at:
    #         self.payed_at = timezone.now()

    #     if self.status == 'SHIPPED' and not self.shipped_at:
    #         self.shipped_at = timezone.now()

    #     if self.status == 'DELIVERED' and not self.delivered_at:
    #         self.delivered_at = timezone.now()
    #     # Finally, save the object
    #     super().save(*args, **kwargs)

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

class Faq(models.Model):
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    show = models.BooleanField(default=True)
    def __str__(self):
        return self.question
    
class Testemonial(models.Model):
    author = models.CharField(max_length=255)
    content = models.TextField()
    def __str__(self):
        return f'Testimonial by {self.author} - {self.content[:100]}...'




    

class Setting(models.Model):
    name = models.CharField(max_length=255)
    home_painting_hero_1= models.ForeignKey(Painting, on_delete=models.CASCADE, related_name='home_painting_1',)
    home_painting_hero_2= models.ForeignKey(Painting, on_delete=models.CASCADE, related_name='home_painting_2', )
    home_painting_hero_3= models.ForeignKey(Painting, on_delete=models.CASCADE, related_name='home_painting_3', )
    home_painting_list_1= models.ForeignKey(Painting, on_delete=models.CASCADE, related_name='home_painting_4',)
    home_painting_list_2= models.ForeignKey(Painting, on_delete=models.CASCADE, related_name='home_painting_5',)
    home_painting_list_3= models.ForeignKey(Painting, on_delete=models.CASCADE, related_name='home_painting_6',)
    home_artist_1= models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='home_artist_1',)
    home_artist_2= models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='home_artist_2',)
    home_artist_3= models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='home_artist_3',)

    home_image_section_1=ProcessedImageField(upload_to='settings/home_image_section_1', processors=[ResizeToFit(800, 800)], format='WEBP', options={'quality': 85})
    become_seller_video=models.FileField(upload_to='settings/become_seller_video')
    

    
    home_story_1_image=ProcessedImageField(upload_to='settings/home_story_1_image', processors=[ResizeToFit(1200, 1200)], format='WEBP', options={'quality': 85})
    home_story_1_title=models.CharField(max_length=255)
    home_story_2_image=ProcessedImageField(upload_to='settings/home_story_2_image', processors=[ResizeToFit(1200, 1200)], format='WEBP', options={'quality': 85})
    home_story_2_title=models.CharField(max_length=255)
    home_story_3_image=ProcessedImageField(upload_to='settings/home_story_3_image', processors=[ResizeToFit(1200, 1200)], format='WEBP', options={'quality': 85})
    home_story_3_title=models.CharField(max_length=255)
    home_story_4_image=ProcessedImageField(upload_to='settings/home_story_4_image', processors=[ResizeToFit(1200, 1200)], format='WEBP', options={'quality': 85})
    home_story_4_title=models.CharField(max_length=255)
    home_story_5_image=ProcessedImageField(upload_to='settings/home_story_5_image', processors=[ResizeToFit(1200, 1200)], format='WEBP', options={'quality': 85})
    home_story_5_title=models.CharField(max_length=255)

    core_value_1_title=models.CharField(max_length=255)
    core_value_1_title_description=models.TextField()
    core_value_1_image=ProcessedImageField(upload_to='settings/core_value_1_image', processors=[ResizeToFit(800, 800)], format='WEBP', options={'quality': 85})
    core_value_2_title=models.CharField(max_length=255)
    core_value_2_title_description=models.TextField()
    core_value_2_image=ProcessedImageField(upload_to='settings/core_value_2_image', processors=[ResizeToFit(800, 800)], format='WEBP', options={'quality': 85})
    core_value_3_title=models.CharField(max_length=255)
    core_value_3_title_description=models.TextField()
    core_value_4_image=ProcessedImageField(upload_to='settings/core_value_3_image', processors=[ResizeToFit(800, 800)], format='WEBP', options={'quality': 85})

    loading = ImageSpecField(source='core_value_1_image',
                          processors=[ResizeToFit(1, 1)],
                          format='WEBP',
                          options={'quality': 55})


    testimony_1=models.ForeignKey(Testemonial, on_delete=models.CASCADE, related_name='testemony_1',)
    testimony_2=models.ForeignKey(Testemonial, on_delete=models.CASCADE,related_name='testemony_2')
    testimony_3=models.ForeignKey(Testemonial, on_delete=models.CASCADE, related_name='testemony_3')
    

    hero_about_us_image=ProcessedImageField(upload_to='settings/hero_about_us_image', processors=[ResizeToFit(1000, 1000)], format='WEBP', options={'quality': 85})
    hero_about_us_description=models.CharField(max_length=100)
    about_image_1=ProcessedImageField(upload_to='settings/about_image_1', processors=[ResizeToFit(800, 800)], format='WEBP', options={'quality': 85})
    about_image_2=ProcessedImageField(upload_to='settings/about_image_2', processors=[ResizeToFit(800, 800)], format='WEBP', options={'quality': 85})
    about_image_3=ProcessedImageField(upload_to='settings/about_image_3', processors=[ResizeToFit(800, 800)], format='WEBP', options={'quality': 85})
    about_story=models.TextField()
    email=models.EmailField()
    address=models.TextField()
    phone=models.CharField(max_length=255)
    facebook=models.URLField(null=True, blank=True)
    twitter=models.URLField(null=True, blank=True)
    instagram=models.URLField(null=True, blank=True)
    pinterest=models.URLField(null=True, blank=True)
    open_hours=models.TextField()

    preview_image=ProcessedImageField(upload_to='settings/preview_image', processors=[ResizeToFit(300, 300)], format='WEBP', options={'quality': 95})
    team=models.ManyToManyField(Artist, related_name='team')

    hero_contact_image=ProcessedImageField(upload_to='settings/hero_contact_image', processors=[ResizeToFit(1000, 1000)], format='WEBP', options={'quality': 95})
    contact_description=models.TextField()
    show=models.BooleanField()


    def save(self, *args, **kwargs):
        if self.show:
            # Set show=False for all other instances
            Setting.objects.filter(show=True).exclude(pk=self.id).update(show=False)
        super(Setting, self).save(*args, **kwargs)


class PrivacyPolicy_paragraph(models.Model):
    Settings = models.ForeignKey(Setting, on_delete=models.CASCADE)
    title=models.CharField(max_length=255)
    paragraph = models.TextField()

class TermsAndConditions_paragraph(models.Model):
    Settings = models.ForeignKey(Setting, on_delete=models.CASCADE)
    title=models.CharField(max_length=255)
    paragraph = models.TextField()

class ContactRequest(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.email}"
    
class SellerRequest(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    business_name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

