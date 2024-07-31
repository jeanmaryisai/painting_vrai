from django.contrib import admin
from .models import Address, Artist, Category, Tag, Painting, Order, OrderItem, Review, Notification


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'address', 'country', 'state', 'zip_code', 'shipping_price', 'is_priced']
    list_filter = ['is_priced', 'country', 'state']
    search_fields = ['first_name', 'last_name', 'address', 'country', 'state', 'zip_code']

class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'birth_date')
    search_fields = ('name',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

class PaintingAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'category', 'price', 'created_at', 'isNew', 'show')
    search_fields = ('title', 'description', 'artist__name', 'category__name', 'tags__name')
    list_filter = ('artist', 'category', 'tags', 'show')
    prepopulated_fields = {'slug': ('title',)}

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('painting', 'quantity')
    can_delete = True

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'status')
    search_fields = ('user__username', 'status')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'painting', 'created_at')
    search_fields = ('user', 'painting__title')
    list_filter = ('created_at',)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    list_filter = ('is_read', 'created_at')

admin.site.register(Artist, ArtistAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Painting, PaintingAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Notification, NotificationAdmin)

